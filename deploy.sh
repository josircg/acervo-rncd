#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ -f deploy.env ]]; then
  set -a
  # shellcheck disable=SC1091
  source deploy.env
  set +a
fi

uv sync --frozen
uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput
exec uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
