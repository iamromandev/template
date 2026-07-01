"""Background task infra — ARQ-based async job processing.

The template ships with ARQ (not Celery) because:
    * Pure async — no sync compatibility layer.
    * Redis-backed (already a deps for caching).
    * Minimal boilerplate vs Celery.

Swap in Celery if you need:
    * Periodic / scheduled tasks (Celery Beat).
    * Complex routing / multiple queues.
    * Brokers besides Redis (RabbitMQ, SQS).

Usage:
    from src.task.jobs.send_email import send_email
    await send_email("user@example.com", "Welcome!")

For the worker process:
    python -m src.task.worker
"""

from src.task.worker import run_worker as run_worker
from src.task.worker import worker_settings as worker_settings

__all__ = ["run_worker", "worker_settings"]
