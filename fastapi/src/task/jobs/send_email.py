"""Example background job — send an email.

Job signatures must be async functions that accept ``ctx`` as the
first positional argument (ARQ injects it automatically).  Additional
args are passed by the caller at enqueue time::

    await send_email(ctx, to="user@example.com", subject="Hi")
"""

from __future__ import annotations

from typing import Any

from loguru import logger


async def send_email(
    ctx: dict[str, Any],
    *,
    to: str,
    subject: str = "",
    body: str = "",
) -> bool:
    """Send an email (stub — wire to your email provider).

    Args:
        ctx: ARQ context (contains ``redis``, ``job_id``, etc.).
        to: Recipient email address.
        subject: Email subject line.
        body: Email body (plain text or HTML).

    Returns:
        True if the email was sent successfully.
    """
    logger.info(
        "Sending email to={} subject='{}' body_len={} [job={}]",
        to,
        subject,
        len(body),
        ctx.get("job_id", "?"),
    )
    # Stub — replace with your email provider (SendGrid, SES, SMTP, …).
    # await email_provider.send(to=to, subject=subject, body=body)
    logger.info("Email sent to={}", to)
    return True


__all__ = ["send_email"]
