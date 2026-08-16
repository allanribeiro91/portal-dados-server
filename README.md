Portal de Dados — API

Backend do Portal de Dados do projeto Irrigação Tocantins. A aplicação fornece uma API
REST para autenticação, gestão de usuários e, futuramente, disponibilização dos produtos
de dados da plataforma.

O projeto utiliza FastAPI, SQLAlchemy e PostgreSQL, com organização modular para separar
rotas, regras de negócio, validações e modelos do banco.

Tecnologias

Python 3.12+

FastAPI

PostgreSQL

SQLAlchemy 2 e Psycopg 3

Pydantic 2 e Pydantic Settings

PyJWT e JWT HS256

Argon2id para hash de senhas

Pytest e Ruff

Funcionalidades implementadas

conexão com PostgreSQL;

cadastro, consulta, atualização e inativação de usuários;

validação e normalização de CPF, e-mail, celular e senha;

login por e-mail ou CPF;

access token JWT;

refresh token rotativo, armazenado apenas como hash no banco;

refresh token enviado em cookie HttpOnly;

logout com revogação da sessão;

controle de acesso por usuário e tipo;

health check, Swagger UI e ReDoc.

Estrutura do projeto

portal-dados-server/
├── app/
│ ├── api/
│ │ └── router.py
│ ├── core/
│ │ ├── config.py
│ │ ├── database.py
│ │ └── security.py
│ ├── modules/
│ │ ├── autenticacao/
│ │ │ ├── dependency.py
│ │ │ ├── model.py
│ │ │ ├── router.py
│ │ │ ├── schema.py
│ │ │ ├── service.py
│ │ │ └── token.py
│ │ ├── health/
│ │ └── usuario/
│ │ ├── model.py
│ │ ├── router.py
│ │ ├── schema.py
│ │ └── service.py
│ └── main.py
├── database/
│ ├── ddl/
│ └── dml/
├── tests/
├── .env.example
├── pyproject.toml
├── requirements.txt
└── README.md

Cada módulo mantém juntos seus modelos, schemas, serviços, dependências e rotas. As
configurações compartilhadas ficam em app/core.

Preparação do ambiente

1. Criar e ativar o ambiente virtual

Windows PowerShell:

python -m venv venv
venv\Scripts\Activate.ps1

Linux ou macOS:

python -m venv venv
source venv/bin/activate

2. Instalar as dependências

python -m pip install --upgrade pip
pip install -r requirements.txt

Alternativamente, usando o pyproject.toml:

pip install -e ".[dev]"

3. Configurar o .env

Copie .env.example para .env e ajuste os valores locais:

# ===================== APPLICATION =====================

APP_NAME=Portal de Dados API
APP_VERSION=0.1.0
APP_ENV=development
APP_DEBUG=true
API_V1_PREFIX=/api/v1

# ====================== DATABASE =======================

DB_DIALECT=postgresql
DB_DRIVER=psycopg
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=sua_senha_local
DB_DATABASE=dbportaldados
DB_SCHEMA=scportaldados
DB_ECHO=false
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# ==================== AUTENTICAÇÃO =====================

JWT_SECRET_KEY=sua_chave_secreta
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_ISSUER=portal-dados-api
JWT_AUDIENCE=portal-dados-frontend
JWT_REFRESH_COOKIE_NAME=portal_refresh_token
JWT_REFRESH_COOKIE_SECURE=false
JWT_REFRESH_COOKIE_SAMESITE=lax

Gere uma chave JWT aleatória:

python -c "import secrets; print(secrets.token_urlsafe(64))"

O .env contém informações sensíveis e não deve ser versionado. O .env.example deve
conter somente valores de exemplo.

Em produção, utilize ao menos:

APP_ENV=production
APP_DEBUG=false
JWT_REFRESH_COOKIE_SECURE=true

Banco de dados

Crie o banco PostgreSQL:

CREATE DATABASE dbportaldados;

Conecte-se ao banco criado e execute os scripts nesta ordem:

database/ddl/001_criar_tabelas_usuario_dominio.sql;

database/dml/001_inserir_dominios_usuario.sql;

database/ddl/002_criar_tabela_sessao_refresh.sql;

o DML do usuário inicial, caso seja utilizado no ambiente.

Os scripts criam e utilizam o schema scportaldados. O usuário configurado em
DB_USERNAME precisa ter acesso ao schema e às tabelas.

A coluna DS_SENHA deve receber somente hashes Argon2id, nunca senhas em texto puro.

Execução

uvicorn app.main:app --reload

API: http://127.0.0.1:8000;

Swagger UI: http://127.0.0.1:8000/docs;

ReDoc: http://127.0.0.1:8000/redoc;

health check: http://127.0.0.1:8000/api/v1/health.

O modo --reload deve ser utilizado apenas em desenvolvimento.

Autenticação

O login aceita e-mail, CPF ou ambos:

{
"ds_email": "usuario@example.com",
"ds_senha": "Senha@Segura123"
}

Ou:

{
"co_cpf": "00011122233",
"ds_senha": "Senha@Segura123"
}

O access token retornado deve ser enviado nas rotas protegidas:

Authorization: Bearer ACCESS_TOKEN

O refresh token fica em cookie HttpOnly e não deve ser armazenado em localStorage.
O frontend deve permitir cookies no login, na renovação e no logout:

fetch(url, {
method: "POST",
credentials: "include",
});

Quando o access token expirar, o frontend chama POST /api/v1/auth/refresh. A API valida
a sessão, revoga o refresh token anterior e emite um novo par de tokens.

Rotas

Autenticação

Método

Rota

Acesso

Finalidade

POST

/api/v1/auth/login

Público

Autenticar por e-mail ou CPF

POST

/api/v1/auth/refresh

Refresh cookie

Renovar a sessão

POST

/api/v1/auth/logout

Refresh cookie

Revogar a sessão

GET

/api/v1/auth/me

Autenticado

Consultar o usuário atual

Usuários

Método

Rota

Acesso

Finalidade

POST

/api/v1/usuarios

Público

Cadastrar usuário comum

GET

/api/v1/usuarios

Administrador ou Master

Listar usuários

GET

/api/v1/usuarios/{usuario_id}

Administrador ou Master

Consultar usuário

PATCH

/api/v1/usuarios/{usuario_id}

Próprio usuário, Administrador ou Master

Atualizar usuário

DELETE

/api/v1/usuarios/{usuario_id}

Administrador ou Master

Inativar usuário

Na listagem, estão disponíveis:

offset: registros ignorados, com padrão 0;

limit: quantidade máxima, com padrão 50 e máximo 100;

incluir_inativos: inclui inativos quando igual a true.

Exemplo:

/api/v1/usuarios?offset=0&limit=50&incluir_inativos=true

O cadastro público deve criar obrigatoriamente um Usuário Comum com status Ativo,
independentemente de valores administrativos enviados pelo cliente.

Na atualização, usuários comuns podem alterar apenas o próprio cadastro e não podem
alterar co_tp_usuario ou co_status. Administradores e Masters podem atualizar outros
usuários e esses campos administrativos.

O DELETE é lógico: o registro não é removido, apenas passa para o status Inativo.

Respostas de erro

Código

Significado

400

Requisição inválida ou regra de negócio não atendida

401

Credencial ausente, inválida ou expirada

403

Usuário autenticado sem permissão

404

Recurso não encontrado

409

Conflito, como CPF ou e-mail já cadastrado

422

Dados incompatíveis com o schema de entrada

Testes

Todos os testes:

pytest -v

Somente autenticação:

pytest tests/test_autenticacao.py -v

Um teste específico:

pytest tests/test_autenticacao.py::test_access_token_contem_dados_do_usuario -v

Os testes unitários validam schemas, normalização, hash de senha, health check e tokens.
Testes de integração devem utilizar um banco exclusivo para testes.

Qualidade de código

ruff check .
ruff format --check .

Para formatar:

ruff format .

Segurança

Não versione .env, senhas, chaves JWT ou tokens;

utilize uma chave JWT longa e diferente por ambiente;

nunca armazene senhas em texto puro;

utilize cookie Secure para o refresh token em produção;

disponibilize a aplicação em produção somente por HTTPS;

não permita que o cadastro público atribua perfis administrativos;

utilize um banco separado nos testes de integração.

Frontend

Este repositório contém exclusivamente o backend. O frontend é uma aplicação independente
que consome esta API por HTTP.

Status do projeto

O projeto está em desenvolvimento. Usuários e autenticação formam a base inicial sobre a
qual serão adicionados os produtos de dados e as demais funcionalidades do Portal.
