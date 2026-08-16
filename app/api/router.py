from fastapi import APIRouter

from app.modules.health.router import router as health_router
from app.modules.usuario.router import router as usuario_router
from app.modules.autenticacao.router import router as autenticacao_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(usuario_router)
api_router.include_router(autenticacao_router)