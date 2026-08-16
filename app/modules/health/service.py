from app.core.config import settings
from app.modules.health.schema import HealthResponse


def get_health_status() -> HealthResponse:
    return HealthResponse(
        status="ok",
        application=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )
