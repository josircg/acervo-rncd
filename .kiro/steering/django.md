# Contexto do Projeto — RNCD Pesquisas

Este é um aplicativo que transforma um XML que contém artigos e notícias em uma base de dados sqlite para que se possa realizar buscas nos registros existentes.

## Stack confirmada

- **Python**: 3.12 (via pyenv)
- **Django**: 3.2.25 (o `pyproject.toml` fixa `Django<4` — NÃO subir para 4.x)
- **Banco**: SQLite
- **Settings module**: `config.settings` (carregado pelo `manage.py`)

## Como rodar comandos

Sempre use o interpretador uv

```bash
uv run manage.py <comando>
```

### Comandos de verificação

```bash
uv run manage.py check
uv run manage.py makemigrations --check --dry-run
```

### Testes

Os testes ainda não foram criados.

### Superusuário de desenvolvimento

Para testar o admin (e verificações de UI via Playwright), existe um
superusuário fixo **apenas no banco local** (`db.sqlite3`, que é gitignored):

- **usuário**: `kiro_admin`
- **senha**: `kiro-dev-2026`

É credencial exclusiva de desenvolvimento — NUNCA deve ser criada em produção.
Se o banco local for recriado, recrie o usuário com:

```bash
uv run python manage.py shell -c "
from django.contrib.auth import get_user_model
U = get_user_model()
u, _ = U.objects.get_or_create(username='kiro_admin', defaults={'is_staff': True, 'is_superuser': True})
u.is_staff = True; u.is_superuser = True
u.set_password('kiro-dev-2026'); u.save()
"
```

Em dev o `ALLOWED_HOSTS` do `config/local.env` aceita `localhost` e
`127.0.0.1`; o admin fica em `/admin/` (ex.: `http://localhost:8000/admin/`).

## Configuração de settings

- Base: `config/settings.py`

## Armadilhas de ambiente


## Arquitetura

App único `pesquisas` (admin padrão do Django).

## Convenções

## Fluxo de trabalho com specs

Para features não-triviais, use o template de spec específico deste projeto:
`#django-spec-template` (em `.kiro/steering/django-spec-template.md`).
