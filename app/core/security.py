from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def gerar_hash_senha(senha: str) -> str:
    return password_hash.hash(senha)


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    return password_hash.verify(senha, hash_armazenado)
