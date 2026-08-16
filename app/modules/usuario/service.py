from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased, joinedload

from app.core.security import gerar_hash_senha
from app.modules.usuario.model import Dominio, Usuario
from app.modules.usuario.schema import UsuarioCreate, UsuarioUpdate


def _usuario_query():
    return select(Usuario).options(
        joinedload(Usuario.status),
        joinedload(Usuario.tipo_usuario),
    )


def _get_usuario_or_404(db: Session, usuario_id: int) -> Usuario:
    usuario = db.scalar(_usuario_query().where(Usuario.co_seq_usuario == usuario_id))
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    return usuario


def _validar_dominio(db: Session, dominio_id: int, nome_grupo: str) -> Dominio:
    dominio_pai = aliased(Dominio)
    dominio = db.scalar(
        select(Dominio)
        .join(dominio_pai, dominio_pai.co_seq_dominio == Dominio.co_dominio)
        .where(
            Dominio.co_seq_dominio == dominio_id,
            dominio_pai.no_dominio == nome_grupo,
        )
    )
    if dominio is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Domínio inválido para {nome_grupo}",
        )
    return dominio


def _get_dominio_por_nome(db: Session, nome_grupo: str, nome_valor: str) -> Dominio:
    dominio_pai = aliased(Dominio)
    dominio = db.scalar(
        select(Dominio)
        .join(dominio_pai, dominio_pai.co_seq_dominio == Dominio.co_dominio)
        .where(
            dominio_pai.no_dominio == nome_grupo,
            Dominio.no_dominio == nome_valor,
        )
    )
    if dominio is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Domínio {nome_grupo}/{nome_valor} não configurado",
        )
    return dominio


def _validar_duplicidade(
    db: Session,
    cpf: str | None,
    email: str | None,
    usuario_id: int | None = None,
) -> None:
    filtros = []
    if cpf is not None:
        filtros.append(Usuario.co_cpf == cpf)
    if email is not None:
        filtros.append(func.lower(Usuario.ds_email) == email.lower())
    if not filtros:
        return

    query = select(Usuario).where(or_(*filtros))
    if usuario_id is not None:
        query = query.where(Usuario.co_seq_usuario != usuario_id)
    existente = db.scalar(query)
    if existente is None:
        return
    if cpf is not None and existente.co_cpf == cpf:
        detalhe = "Já existe um usuário cadastrado com este CPF"
    else:
        detalhe = "Já existe um usuário cadastrado com este e-mail"
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detalhe)


def create_usuario(db: Session, payload: UsuarioCreate) -> Usuario:
    email = str(payload.ds_email).lower()
    _validar_duplicidade(db, payload.co_cpf, email)

    status_usuario = (
        _validar_dominio(db, payload.co_status, "Status do Usuário")
        if payload.co_status is not None
        else _get_dominio_por_nome(db, "Status do Usuário", "Ativo")
    )
    _validar_dominio(db, payload.co_tp_usuario, "Tipo de Usuário")

    usuario = Usuario(
        co_cpf=payload.co_cpf,
        no_nome=payload.no_nome,
        ds_email=email,
        ds_celular=payload.ds_celular,
        ds_senha=gerar_hash_senha(payload.ds_senha),
        co_status=status_usuario.co_seq_dominio,
        co_tp_usuario=payload.co_tp_usuario,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF ou e-mail já cadastrado",
        ) from error
    return _get_usuario_or_404(db, usuario.co_seq_usuario)


def get_usuarios(
    db: Session,
    offset: int = 0,
    limit: int = 50,
    incluir_inativos: bool = False,
) -> list[Usuario]:
    query = _usuario_query().order_by(Usuario.no_nome).offset(offset).limit(limit)
    if not incluir_inativos:
        inativo = _get_dominio_por_nome(db, "Status do Usuário", "Inativo")
        query = query.where(Usuario.co_status != inativo.co_seq_dominio)
    return list(db.scalars(query).unique().all())


def get_usuario_by_id(db: Session, usuario_id: int) -> Usuario:
    return _get_usuario_or_404(db, usuario_id)


def update_usuario(db: Session, usuario_id: int, payload: UsuarioUpdate) -> Usuario:
    usuario = _get_usuario_or_404(db, usuario_id)
    dados = payload.model_dump(exclude_unset=True)

    email = str(dados["ds_email"]).lower() if "ds_email" in dados else None
    _validar_duplicidade(db, dados.get("co_cpf"), email, usuario_id)

    if "co_status" in dados:
        _validar_dominio(db, dados["co_status"], "Status do Usuário")
    if "co_tp_usuario" in dados:
        _validar_dominio(db, dados["co_tp_usuario"], "Tipo de Usuário")
    if email is not None:
        dados["ds_email"] = email
    if "ds_senha" in dados:
        dados["ds_senha"] = gerar_hash_senha(dados["ds_senha"])

    for campo, valor in dados.items():
        setattr(usuario, campo, valor)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF ou e-mail já cadastrado",
        ) from error
    return _get_usuario_or_404(db, usuario_id)


def soft_delete_usuario(db: Session, usuario_id: int) -> None:
    usuario = _get_usuario_or_404(db, usuario_id)
    inativo = _get_dominio_por_nome(db, "Status do Usuário", "Inativo")
    if usuario.co_status != inativo.co_seq_dominio:
        usuario.co_status = inativo.co_seq_dominio
        db.commit()
