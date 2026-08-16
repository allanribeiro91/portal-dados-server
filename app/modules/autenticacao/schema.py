import re

from pydantic import BaseModel, EmailStr, Field, model_validator


class LoginRequest(BaseModel):
    ds_email: EmailStr | None = None
    co_cpf: str | None = None
    ds_senha: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def validar_identificador(self) -> "LoginRequest":
        if self.ds_email is None and self.co_cpf is None:
            raise ValueError("Informe o e-mail ou o CPF")
        if self.co_cpf is not None:
            cpf = re.sub(r"\D", "", self.co_cpf)
            if len(cpf) != 11:
                raise ValueError("CPF deve possuir 11 dígitos")
            self.co_cpf = cpf
        return self


class UsuarioAutenticadoResponse(BaseModel):
    co_seq_usuario: int
    no_nome: str
    ds_email: EmailStr
    co_tp_usuario: int
    no_tipo_usuario: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario: UsuarioAutenticadoResponse