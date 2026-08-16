from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.security import gerar_hash_senha, verificar_senha
from app.modules.autenticacao.model import SessaoRefresh
from app.modules.autenticacao.schema import LoginRequest, UsuarioAutenticadoResponse
from app.modules.autenticacao.token import criar_access_token
from app.modules.usuario.model import Usuario

DUMMY_PASSWORD_HASH = gerar_hash_senha(token_urlsafe(32))


@dataclass
class AuthResult:
    access_token: str
    expires_in: int
    refresh_token: str
    usuario: UsuarioAutenticadoResponse
    sessao: SessaoRefresh


def _unauthorized(detail: str = "E-mail/CPF ou senha inválidos") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _hash_refresh_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def _query_usuario():
    return select(Usuario).options(
        joinedload(Usuario.status),
        joinedload(Usuario.tipo_usuario),
    )


def _usuario_response(usuario: Usuario) -> UsuarioAutenticadoResponse:
    return UsuarioAutenticadoResponse(
        co_seq_usuario=usuario.co_seq_usuario,
        no_nome=usuario.no_nome,
        ds_email=usuario.ds_email,
        co_tp_usuario=usuario.co_tp_usuario,
        no_tipo_usuario=usuario.tipo_usuario.no_dominio,
    )


def _nova_sessao(
    usuario_id: int,
    refresh_token: str,
    ip: str | None,
    user_agent: str | None,
) -> SessaoRefresh:
    return SessaoRefresh(
        co_usuario=usuario_id,
        ds_token_hash=_hash_refresh_token(refresh_token),
        dt_expiracao=datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days),
        ds_ip=ip,
        ds_user_agent=user_agent[:500] if user_agent else None,
    )


def _emitir_tokens(
    db: Session,
    usuario: Usuario,
    ip: str | None,
    user_agent: str | None,
) -> AuthResult:
    access_token, expires_in = criar_access_token(usuario)
    refresh_token = token_urlsafe(48)
    sessao = _nova_sessao(usuario.co_seq_usuario, refresh_token, ip, user_agent)
    db.add(sessao)
    return AuthResult(
        access_token=access_token,
        expires_in=expires_in,
        refresh_token=refresh_token,
        usuario=_usuario_response(usuario),
        sessao=sessao,
    )


def login(
    db: Session,
    payload: LoginRequest,
    ip: str | None,
    user_agent: str | None,
) -> AuthResult:
    query = _query_usuario()
    if payload.ds_email is not None:
        query = query.where(func.lower(Usuario.ds_email) == str(payload.ds_email).lower())
    if payload.co_cpf is not None:
        query = query.where(Usuario.co_cpf == payload.co_cpf)

    usuario = db.scalar(query)
    hash_armazenado = usuario.ds_senha if usuario is not None else DUMMY_PASSWORD_HASH
    senha_valida = verificar_senha(payload.ds_senha, hash_armazenado)

    if usuario is None or not senha_valida:
        raise _unauthorized()
    if usuario.status.no_dominio != "Ativo":
        raise _unauthorized("Usuário sem acesso à aplicação")

    resultado = _emitir_tokens(db, usuario, ip, user_agent)
    db.commit()
    return resultado


def renovar(
    db: Session,
    refresh_token: str,
    ip: str | None,
    user_agent: str | None,
) -> AuthResult:
    agora = datetime.now(UTC)
    sessao = db.scalar(
        select(SessaoRefresh)
        .where(SessaoRefresh.ds_token_hash == _hash_refresh_token(refresh_token))
        .with_for_update()
    )
    if sessao is None:
        raise _unauthorized("Refresh token inválido")

    if sessao.dt_revogacao is not None:
        db.execute(
            update(SessaoRefresh)
            .where(
                SessaoRefresh.co_usuario == sessao.co_usuario,
                SessaoRefresh.dt_revogacao.is_(None),
            )
            .values(dt_revogacao=agora)
        )
        db.commit()
        raise _unauthorized("Refresh token reutilizado; sessões revogadas")

    if sessao.dt_expiracao <= agora:
        sessao.dt_revogacao = agora
        db.commit()
        raise _unauthorized("Refresh token expirado")

    usuario = db.scalar(_query_usuario().where(Usuario.co_seq_usuario == sessao.co_usuario))
    if usuario is None or usuario.status.no_dominio != "Ativo":
        sessao.dt_revogacao = agora
        db.commit()
        raise _unauthorized("Usuário sem acesso à aplicação")

    resultado = _emitir_tokens(db, usuario, ip, user_agent)
    db.flush()
    sessao.dt_revogacao = agora
    sessao.co_sessao_substituta = resultado.sessao.co_seq_sessao
    db.commit()
    return resultado


def logout(db: Session, refresh_token: str | None) -> None:
    if not refresh_token:
        return
    sessao = db.scalar(
        select(SessaoRefresh).where(
            SessaoRefresh.ds_token_hash == _hash_refresh_token(refresh_token),
            SessaoRefresh.dt_revogacao.is_(None),
        )
    )
    if sessao is not None:
        sessao.dt_revogacao = datetime.now(UTC)
        db.commit()


def revogar_sessoes_usuario(db: Session, usuario_id: int) -> None:
    db.execute(
        update(SessaoRefresh)
        .where(
            SessaoRefresh.co_usuario == usuario_id,
            SessaoRefresh.dt_revogacao.is_(None),
        )
        .values(dt_revogacao=datetime.now(UTC))
    )