from backend.config.settings import settings


celery_app = None
if settings.USE_DISTRIBUTED_QUEUE and settings.CELERY_BROKER_URL:
    try:
        from celery import Celery

        celery_app = Celery(
            "grievance_backend",
            broker=settings.CELERY_BROKER_URL,
            backend=settings.CELERY_RESULT_BACKEND or settings.CELERY_BROKER_URL,
        )
    except Exception:
        celery_app = None
