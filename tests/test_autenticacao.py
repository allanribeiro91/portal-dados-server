from types import SimpleNamespace

import jwt
import pytest
from pydantic import ValidationError

from app.modules.autenticacao.schema import LoginRequest
from app.modules.autenticacao.token import (
    criar_access_token,
    decodificar_access_token,
)


def test_login_aceita_email() -> None:
    payload = LoginRequest(
        ds_email="usuario@example.com",
        ds_senha="senha",
    )

    assert str(payload.ds_email) == "usuario@example.com"
    assert payload.co_cpf is None


def test_login_aceita_cpf_e_remove_formatacao() -> None:
    payload = LoginRequest(
        co_cpf="000.111.222-33",
        ds_senha="senha",
    )

    assert payload.co_cpf == "00011122233"
    assert payload.ds_email is None


def test_login_aceita_email_e_cpf() -> None:
    payload = LoginRequest(
        ds_email="usuario@example.com",
        co_cpf="000.111.222-33",
        ds_senha="senha",
    )

    assert str(payload.ds_email) == "usuario@example.com"
    assert payload.co_cpf == "00011122233"


def test_login_exige_identificador() -> None:
    with pytest.raises(
        ValidationError,
        match="Informe o e-mail ou o CPF",
    ):
        LoginRequest(ds_senha="senha")


def test_login_rejeita_cpf_com_tamanho_invalido() -> None:
    with pytest.raises(
        ValidationError,
        match="CPF deve possuir 11 dígitos",
    ):
        LoginRequest(
            co_cpf="123456789",
            ds_senha="senha",
        )


def test_login_rejeita_email_invalido() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(
            ds_email="email-invalido",
            ds_senha="senha",
        )


def test_login_exige_senha() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(
            ds_email="usuario@example.com",
            ds_senha="",
        )


def test_access_token_contem_dados_do_usuario() -> None:
    usuario = SimpleNamespace(
        co_seq_usuario=1,
        ds_email="usuario@example.com",
        no_nome="Usuário Teste",
        co_tp_usuario=2,
        tipo_usuario=SimpleNamespace(
            no_dominio="Usuário Comum",
        ),
    )

    token, expires_in = criar_access_token(usuario)
    payload = decodificar_access_token(token)

    assert expires_in > 0
    assert payload["sub"] == "1"
    assert payload["email"] == "usuario@example.com"
    assert payload["nome"] == "Usuário Teste"
    assert payload["co_tp_usuario"] == 2
    assert payload["tipo_usuario"] == "Usuário Comum"
    assert payload["type"] == "access"

    assert "jti" in payload
    assert "iat" in payload
    assert "nbf" in payload
    assert "exp" in payload
    assert "iss" in payload
    assert "aud" in payload


def test_token_invalido_e_rejeitado() -> None:
    with pytest.raises(jwt.InvalidTokenError):
        decodificar_access_token("token-invalido")