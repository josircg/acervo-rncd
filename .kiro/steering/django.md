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

## Configuração de settings

- Base: `config/settings.py`

## Armadilhas de ambiente


## Arquitetura

App único `pesquisas` (admin padrão do Django).

## Convenções

## Fluxo de trabalho com specs

Para features não-triviais, use o template de spec específico deste projeto:
`#django-spec-template` (em `.kiro/steering/django-spec-template.md`).
