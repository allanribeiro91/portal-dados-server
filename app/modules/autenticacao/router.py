from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.modules.autenticacao.dependency import get_current_user
from app.modules.autenticacao.schema import (
    LoginRequest,
    TokenResponse,
    UsuarioAutenticadoResponse,
)
from app.modules.autenticacao.service import login, logout, renovar
from app.modules.usuario.model import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticação"])
DatabaseSession = Annotated[Session, Depends(get_db)]


def _client_info(request: Request) -> tuple[str | None, str | None]:
    ip = request.client.host if request.client else None
    return ip, request.headers.get("user-agent")


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.jwt_refresh_cookie_name,
        value=refresh_token,
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
        secure=settings.jwt_refresh_cookie_secure,
        httponly=True,
        samesite=settings.jwt_refresh_cookie_samesite,
    )


@router.post("/login", response_model=TokenResponse)
def login_route(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: DatabaseSession,
):
    resultado = login(db, payload, *_client_info(request))
    _set_refresh_cookie(response, resultado.refresh_token)
    return TokenResponse(
        access_token=resultado.access_token,
        expires_in=resultado.expires_in,
        usuario=resultado.usuario,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_route(request: Request, response: Response, db: DatabaseSession):
    refresh_token = request.cookies.get(settings.jwt_refresh_cookie_name)
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token não informado",
        )

    resultado = renovar(db, refresh_token, *_client_info(request))
    _set_refresh_cookie(response, resultado.refresh_token)
    return TokenResponse(
        access_token=resultado.access_token,
        expires_in=resultado.expires_in,
        usuario=resultado.usuario,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_route(request: Request, response: Response, db: DatabaseSession) -> Response:
    logout(db, request.cookies.get(settings.jwt_refresh_cookie_name))
    response.delete_cookie(
        settings.jwt_refresh_cookie_name,
        path="/api/v1/auth",
        secure=settings.jwt_refresh_cookie_secure,
        httponly=True,
        samesite=settings.jwt_refresh_cookie_samesite,
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=UsuarioAutenticadoResponse)
def me(usuario: Annotated[Usuario, Depends(get_current_user)]):
    return UsuarioAutenticadoResponse(
        co_seq_usuario=usuario.co_seq_usuario,
        no_nome=usuario.no_nome,
        ds_email=usuario.ds_email,
        co_tp_usuario=usuario.co_tp_usuario,
        no_tipo_usuario=usuario.tipo_usuario.no_dominio,
    )