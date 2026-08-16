from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.modules.autenticacao.token import decodificar_access_token
from app.modules.usuario.model import Usuario

bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized(detail: str = "Credenciais inválidas") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized("Token de acesso não informado")

    try:
        payload = decodificar_access_token(credentials.credentials)
        usuario_id = int(payload["sub"])
    except jwt.ExpiredSignatureError as error:
        raise _unauthorized("Token de acesso expirado") from error
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as error:
        raise _unauthorized() from error

    usuario = db.scalar(
        select(Usuario)
        .options(joinedload(Usuario.status), joinedload(Usuario.tipo_usuario))
        .where(Usuario.co_seq_usuario == usuario_id)
    )
    if usuario is None or usuario.status.no_dominio != "Ativo":
        raise _unauthorized("Usuário sem acesso à aplicação")
    return usuario


def requer_tipos_usuario(*tipos_permitidos: str) -> Callable:
    def dependency(usuario: Annotated[Usuario, Depends(get_current_user)]) -> Usuario:
        if usuario.tipo_usuario.no_dominio not in tipos_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário sem permissão para esta operação",
            )
        return usuario

    return dependency