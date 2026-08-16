from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

from app.core.config import settings
from app.modules.usuario.model import Usuario


def criar_access_token(usuario: Usuario) -> tuple[str, int]:
    agora = datetime.now(UTC)
    duracao = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": str(usuario.co_seq_usuario),
        "email": usuario.ds_email,
        "nome": usuario.no_nome,
        "co_tp_usuario": usuario.co_tp_usuario,
        "tipo_usuario": usuario.tipo_usuario.no_dominio,
        "jti": str(uuid4()),
        "type": "access",
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": agora,
        "nbf": agora,
        "exp": agora + duracao,
    }
    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return token, int(duracao.total_seconds())


def decodificar_access_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
        options={
            "require": [
                "sub",
                "email",
                "nome",
                "co_tp_usuario",
                "tipo_usuario",
                "jti",
                "type",
                "iat",
                "nbf",
                "exp",
                "iss",
                "aud",
            ]
        },
    )
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Tipo de token inválido")
    return payload