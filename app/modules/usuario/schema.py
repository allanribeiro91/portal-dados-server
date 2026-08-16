import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


def validar_cpf(cpf: str | None) -> str | None:
    if cpf is None:
        return None
    cpf = re.sub(r"\D", "", cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValueError("CPF inválido")

    for tamanho in (9, 10):
        soma = sum(int(cpf[indice]) * (tamanho + 1 - indice) for indice in range(tamanho))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[tamanho]):
            raise ValueError("CPF inválido")
    return cpf


def normalizar_nome(nome: str | None) -> str | None:
    if nome is None:
        return None
    nome = " ".join(nome.split())
    if len(nome) < 2:
        raise ValueError("Nome deve possuir pelo menos 2 caracteres")
    return nome


def normalizar_celular(celular: str | None) -> str | None:
    if celular is None:
        return None
    digitos = re.sub(r"\D", "", celular)
    if not 10 <= len(digitos) <= 13:
        raise ValueError("Celular deve possuir entre 10 e 13 dígitos")
    return digitos


def validar_senha(senha: str | None) -> str | None:
    if senha is None:
        return None
    if len(senha) < 12:
        raise ValueError("Senha deve possuir pelo menos 12 caracteres")
    if len(senha) > 128:
        raise ValueError("Senha deve possuir no máximo 128 caracteres")
    regras = (
        (r"[a-z]", "uma letra minúscula"),
        (r"[A-Z]", "uma letra maiúscula"),
        (r"\d", "um número"),
        (r"[^A-Za-z0-9]", "um caractere especial"),
    )
    ausentes = [mensagem for padrao, mensagem in regras if not re.search(padrao, senha)]
    if ausentes:
        raise ValueError(f"Senha deve conter {', '.join(ausentes)}")
    return senha


class UsuarioCreate(BaseModel):
    co_cpf: str
    no_nome: str = Field(min_length=2, max_length=200)
    ds_email: EmailStr
    ds_celular: str | None = None
    ds_senha: str
    co_status: int | None = Field(default=None, gt=0)
    co_tp_usuario: int = Field(gt=0)

    _validar_cpf = field_validator("co_cpf")(validar_cpf)
    _normalizar_nome = field_validator("no_nome")(normalizar_nome)
    _normalizar_celular = field_validator("ds_celular")(normalizar_celular)
    _validar_senha = field_validator("ds_senha")(validar_senha)


class UsuarioUpdate(BaseModel):
    co_cpf: str | None = None
    no_nome: str | None = Field(default=None, min_length=2, max_length=200)
    ds_email: EmailStr | None = None
    ds_celular: str | None = None
    ds_senha: str | None = None
    co_status: int | None = Field(default=None, gt=0)
    co_tp_usuario: int | None = Field(default=None, gt=0)

    _validar_cpf = field_validator("co_cpf")(validar_cpf)
    _normalizar_nome = field_validator("no_nome")(normalizar_nome)
    _normalizar_celular = field_validator("ds_celular")(normalizar_celular)
    _validar_senha = field_validator("ds_senha")(validar_senha)

    @model_validator(mode="after")
    def validate_update(self) -> "UsuarioUpdate":
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualização")

        campos_obrigatorios = {
            "co_cpf",
            "no_nome",
            "ds_email",
            "ds_senha",
            "co_status",
            "co_tp_usuario",
        }
        campos_nulos = [
            campo
            for campo in campos_obrigatorios.intersection(self.model_fields_set)
            if getattr(self, campo) is None
        ]
        if campos_nulos:
            raise ValueError(f"Campos não podem ser nulos: {', '.join(sorted(campos_nulos))}")
        return self


class DominioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    co_seq_dominio: int
    no_dominio: str
    ds_dominio: str | None


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    co_seq_usuario: int
    co_cpf: str
    no_nome: str
    ds_email: EmailStr
    ds_celular: str | None
    dt_registro: datetime
    dt_ultima_atualizacao: datetime
    co_status: int
    co_tp_usuario: int
    status: DominioResponse
    tipo_usuario: DominioResponse
