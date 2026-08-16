from fastapi import APIRouter

from app.modules.health.schema import HealthResponse
from app.modules.health.service import get_health_status

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse, summary="Verificar disponibilidade da API")
def health_check() -> HealthResponse:
    return get_health_status()
