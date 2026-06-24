#!/usr/bin/env bash

echo "Rodando migrações do banco..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor Gunicorn..."
gunicorn core.wsgi --bind 0.0.0.0:8000