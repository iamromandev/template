from tortoise import fields

from src.core.base import Base


class HealthCheckLog(Base):
    """Audit log for health check executions.

    Demonstrates a self-contained model within the health module.
    Every health check writes a row so the system can track uptime
    history without relying on external observability tools.
    """

    status = fields.CharField(max_length=20)
    response_time_ms = fields.FloatField(null=True)
    db_version = fields.TextField(null=True)

    class Meta:
        table = "health_check_log"
