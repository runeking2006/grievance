from concurrent.futures import ThreadPoolExecutor
from email.message import EmailMessage
import smtplib

from backend.config.settings import settings
from backend.services.observability import metrics, notify_logger, timed

_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="notify")


def _deliver_notification(user_email: str, message: str) -> None:
    with timed("notifications.delivery"):
        if settings.SMTP_HOST and settings.SMTP_FROM_EMAIL:
            email = EmailMessage()
            email["Subject"] = "Grievance System Update"
            email["From"] = settings.SMTP_FROM_EMAIL
            email["To"] = user_email
            email.set_content(message)

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
                if settings.SMTP_USE_TLS:
                    smtp.starttls()
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                smtp.send_message(email)
            notify_logger.info(
                "notification_sent",
                extra={"extra_fields": {"user_email": user_email, "channel": "smtp"}},
            )
            metrics.increment("notifications.sent")
            return

        print(f"Notify {user_email}: {message}")
        notify_logger.info(
            "notification_sent",
            extra={"extra_fields": {"user_email": user_email, "channel": "console"}},
        )
        metrics.increment("notifications.sent")


def send_notification(user_email: str | None, message: str) -> None:
    if not user_email:
        metrics.increment("notifications.skipped")
        return
    _executor.submit(_deliver_notification, user_email, message)
