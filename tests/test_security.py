from app.core.security import gerar_hash_senha, verificar_senha


def test_gerar_e_verificar_hash_argon2id() -> None:
    senha = "Senha@Segura123"
    hash_gerado = gerar_hash_senha(senha)

    assert hash_gerado.startswith("$argon2id$")
    assert verificar_senha(senha, hash_gerado) is True
    assert verificar_senha("SenhaIncorreta@123", hash_gerado) is False
