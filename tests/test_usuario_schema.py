import pytest
from pydantic import ValidationError

from app.modules.usuario.schema import UsuarioCreate, UsuarioUpdate


def test_create_normaliza_dados() -> None:
    usuario = UsuarioCreate(
        co_cpf="529.982.247-25",
        no_nome="  Maria   da Silva ",
        ds_email="MARIA@example.com",
        ds_celular="(61) 99999-9999",
        ds_senha="Senha@Segura123",
        co_tp_usuario=2,
    )

    assert usuario.co_cpf == "52998224725"
    assert usuario.no_nome == "Maria da Silva"
    assert usuario.ds_celular == "61999999999"


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("co_cpf", "111.111.111-11"),
        ("ds_email", "email-invalido"),
        ("ds_celular", "123"),
        ("ds_senha", "fraca"),
    ],
)
def test_create_rejeita_dados_invalidos(campo: str, valor: str) -> None:
    dados = {
        "co_cpf": "52998224725",
        "no_nome": "Maria da Silva",
        "ds_email": "maria@example.com",
        "ds_celular": "61999999999",
        "ds_senha": "Senha@Segura123",
        "co_tp_usuario": 2,
    }
    dados[campo] = valor

    with pytest.raises(ValidationError):
        UsuarioCreate(**dados)


def test_update_exige_ao_menos_um_campo() -> None:
    with pytest.raises(ValidationError):
        UsuarioUpdate()


def test_update_permite_remover_celular() -> None:
    usuario = UsuarioUpdate(ds_celular=None)
    assert usuario.ds_celular is None
