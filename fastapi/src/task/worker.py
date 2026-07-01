"""ARQ worker setup — run via ``python -m src.task.worker``.

Connects to Redis, registers job functions from ``src.task.jobs``,
and starts a blocking worker loop.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger

from src.config import get_settings


@dataclass
class WorkerSettings:
    """Settings for the ARQ worker.

    These are consumed by ``arq.Worker`` via the ``functions`` and
    ``redis_settings`` params.  Override via environment variables.
    """

    redis_host: str = field(default_factory=lambda: get_settings().redis_host)
    redis_port: int = field(default_factory=lambda: get_settings().redis_port)
    redis_db: int = field(default_factory=lambda: get_settings().redis_db)
    poll_delay: float = 0.5
    max_jobs: int = 10
    burst: bool = False


worker_settings = WorkerSettings()


async def run_worker() -> None:
    """Start the ARQ worker (blocking).

    Called from ``if __name__ == '__main__'`` below, or from a CLI
    entry point.

    Requires the ``arq`` package — install with ``uv sync --group tasks``
    or ``pip install arq``.
    """
    try:
        import arq
    except ImportError:
        logger.warning(
            "arq is not installed. Install it with 'uv sync --group tasks' or 'pip install arq' to run background jobs."
        )
        return

    redis_settings = arq.connections.RedisSettings(
        host=worker_settings.redis_host,
        port=worker_settings.redis_port,
        database=worker_settings.redis_db,
    )

    from src.task.jobs import job_functions

    worker = arq.Worker(
        functions=job_functions,
        redis_settings=redis_settings,
        poll_delay=worker_settings.poll_delay,
        max_jobs=worker_settings.max_jobs,
        burst=worker_settings.burst,
    )
    logger.info("ARQ worker starting — poll_delay={}", worker_settings.poll_delay)
    await worker.run()


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_worker())


__all__ = ["WorkerSettings", "run_worker", "worker_settings"]
