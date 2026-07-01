"""ARQ job registry — every async function in this module is auto-discovered.

Each job function receives a ``ctx: arq.ctx`` dict as the first argument
(contains ``redis``, ``redis_pool``, ``job_id``, ``job_try``).  The
``job_functions`` list is consumed by ``arq.Worker(functions=...)``.
"""

from __future__ import annotations

from src.task.jobs.send_email import send_email

# All job functions that the ARQ worker should discover.
job_functions = [
    send_email,
]

__all__ = ["job_functions"]
