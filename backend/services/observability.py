import json
import logging
import time
from collections import defaultdict
from collections.abc import Callable
from contextlib import contextmanager
from threading import Lock

from fastapi import Request, Response

from backend.config.settings import settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
        }
        if hasattr(record, "extra_fields"):
            payload.update(record.extra_fields)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    root = logging.getLogger()
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root.setLevel(level)

    if root.handlers:
        for handler in root.handlers:
            handler.setLevel(level)
            handler.setFormatter(JsonFormatter())
        return

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class MetricsRegistry:
    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)
        self._timers: dict[str, list[float]] = defaultdict(list)
        self._gauges: dict[str, float] = {}
        self._lock = Lock()

    def increment(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] += value

    def observe(self, name: str, value: float) -> None:
        with self._lock:
            self._timers[name].append(value)

    def set_gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = value

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            timers = {
                key: {
                    "count": len(values),
                    "avg_ms": round((sum(values) / len(values)) * 1000, 2) if values else 0.0,
                    "max_ms": round(max(values) * 1000, 2) if values else 0.0,
                }
                for key, values in self._timers.items()
            }
            return {
                "counters": dict(self._counters),
                "timers": timers,
                "gauges": dict(self._gauges),
            }


metrics = MetricsRegistry()
app_logger = get_logger("backend.app")
queue_logger = get_logger("backend.queue")
auth_logger = get_logger("backend.auth")
notify_logger = get_logger("backend.notify")


@contextmanager
def timed(metric_name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        metrics.observe(metric_name, time.perf_counter() - start)


async def request_metrics_middleware(
    request: Request,
    call_next: Callable[[Request], Response],
) -> Response:
    path = request.url.path
    method = request.method
    start = time.perf_counter()
    metrics.increment("http.requests.total")

    try:
        response = await call_next(request)
    except Exception:
        metrics.increment("http.requests.failed")
        app_logger.exception(
            "request_failed",
            extra={"extra_fields": {"method": method, "path": path}},
        )
        raise

    duration = time.perf_counter() - start
    metrics.observe("http.request.duration", duration)
    metrics.increment(f"http.response.status.{response.status_code}")
    response.headers["X-Process-Time-Ms"] = str(round(duration * 1000, 2))

    app_logger.info(
        "request_complete",
        extra={
            "extra_fields": {
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            }
        },
    )
    return response
