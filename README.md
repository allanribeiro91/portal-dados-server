# Portal de Dados — Backend

Backend do Portal de Dados, construído com FastAPI e organizado por módulos de negócio.

## Requisitos

- Python 3.12 ou superior

## Instalação

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Copie `.env.example` para `.env` e, se necessário, ajuste as configurações.

Antes de iniciar a API, crie o banco PostgreSQL e execute, nesta ordem:

1. `database/ddl/001_criar_tabelas_usuario_dominio.sql`
2. `database/dml/001_inserir_dominios_usuario.sql`

## Execução

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`. A documentação interativa estará em:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/api/v1/health`

## Rotas de usuários

| Método | Rota | Operação |
| --- | --- | --- |
| `POST` | `/api/v1/usuarios` | Cadastrar usuário |
| `GET` | `/api/v1/usuarios` | Listar usuários |
| `GET` | `/api/v1/usuarios/{usuario_id}` | Consultar usuário |
| `PATCH` | `/api/v1/usuarios/{usuario_id}` | Atualizar parcialmente |
| `DELETE` | `/api/v1/usuarios/{usuario_id}` | Inativar usuário |

Por padrão, a listagem não retorna usuários inativos. Para incluí-los, utilize
`?incluir_inativos=true`. Os parâmetros `offset` e `limit` permitem paginação.

## Testes e qualidade

```bash
pytest
ruff check .
ruff format --check .
```

## Estrutura inicial

```text
portal-dados-server/
├── app/
│   ├── api/
│   │   └── router.py
│   ├── core/
│   │   └── config.py
│   ├── modules/
│   │   └── health/
│   │       ├── router.py
│   │       ├── schema.py
│   │       └── service.py
│   └── main.py
├── tests/
│   └── test_health.py
├── .env.example
└── pyproject.toml
```

Cada domínio da aplicação deverá ser criado dentro de `app/modules`, mantendo juntos seus
arquivos de rota, schemas, modelos e serviços. Arquivos que não se aplicam a um módulo não
precisam ser criados antecipadamente.
