from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.autenticacao.dependency import (
    requer_tipos_usuario,
    get_current_user,
)
from app.modules.usuario.schema import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)
from app.modules.usuario.service import (
    create_usuario,
    get_usuario_by_id,
    get_usuarios,
    soft_delete_usuario,
    update_usuario,
)
from app.modules.usuario.model import Usuario

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]

ApenasAdministradorOuMaster = Depends(
    requer_tipos_usuario("Administrador", "Master")
)

UsuarioAtual = Annotated[
    Usuario,
    Depends(get_current_user),
]


# ROTA PÚBLICA
@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    payload: UsuarioCreate,
    db: DatabaseSession,
):
    return create_usuario(db, payload)


# ROTAS PROTEGIDAS
@router.get(
    "",
    response_model=list[UsuarioResponse],
    dependencies=[ApenasAdministradorOuMaster],
)
def get_all(
    db: DatabaseSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    incluir_inativos: bool = False,
):
    return get_usuarios(
        db,
        offset,
        limit,
        incluir_inativos,
    )


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    dependencies=[ApenasAdministradorOuMaster],
)
def get_by_id(
    usuario_id: int,
    db: DatabaseSession,
):
    return get_usuario_by_id(db, usuario_id)


@router.patch(
    "/{usuario_id}",
    response_model=UsuarioResponse,
)
def update(
    usuario_id: int,
    payload: UsuarioUpdate,
    db: DatabaseSession,
    usuario_atual: UsuarioAtual,
):
    eh_proprio_usuario = (
        usuario_atual.co_seq_usuario == usuario_id
    )

    eh_administrador_ou_master = (
        usuario_atual.tipo_usuario.no_dominio
        in {"Administrador", "Master"}
    )

    if not eh_proprio_usuario and not eh_administrador_ou_master:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para atualizar este usuário.",
        )

    campos_restritos = {
        "co_tp_usuario",
        "co_status",
    }

    if (
        eh_proprio_usuario
        and not eh_administrador_ou_master
        and payload.model_fields_set & campos_restritos
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Apenas Administradores ou Masters podem alterar "
                "o tipo ou o status do usuário."
            ),
        )

    return update_usuario(
        db,
        usuario_id,
        payload,
    )

@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[ApenasAdministradorOuMaster],
)
def delete(
    usuario_id: int,
    db: DatabaseSession,
) -> Response:
    soft_delete_usuario(db, usuario_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )