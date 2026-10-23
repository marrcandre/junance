.DEFAULT_GOAL := help

UV_ENV = set -a; if [ -f .env ]; then . ./.env; fi; set +a;

.PHONY: help sync lock upgrade tree add add-dev remove \
	dev dev-base check-django createsuperuser makemigrations migrate migrations \
	shell test test-cov lint lint-fix format format-check quality \
	python python-install python-pin \
	up down restart logs db-up db-down db-shell \
	collectstatic deploy-check

# ============================================================================
# Ajuda
# ============================================================================

help:
	@echo "Junance - comandos disponíveis:"
	@echo ""
	@echo "Ambiente e dependências (uv):"
	@echo "  make sync                    Sincroniza o ambiente estritamente conforme uv.lock"
	@echo "  make lock                    Atualiza/resolução do uv.lock"
	@echo "  make upgrade                 Atualiza dependências e sincroniza o ambiente"
	@echo "  make tree                    Mostra a árvore de dependências"
	@echo "  make add package=PACOTE      Adiciona dependência de produção"
	@echo "  make add-dev package=PACOTE  Adiciona dependência de desenvolvimento"
	@echo "  make remove package=PACOTE   Remove uma dependência"
	@echo ""
	@echo "Django e testes (execução local):"
	@echo "  make dev                     Inicia Django em 127.0.0.1:8000"
	@echo "  make dev-base                Inicia Django em 0.0.0.0:8000"
	@echo "  make check-django            Executa django check"
	@echo "  make createsuperuser         Cria um superusuário"
	@echo "  make makemigrations          Cria migrations"
	@echo "  make migrate                 Aplica migrations"
	@echo "  make migrations              Cria e aplica migrations"
	@echo "  make shell                   Abre o Django Shell"
	@echo "  make test                    Executa pytest"
	@echo "  make test-cov                Executa pytest com cobertura"
	@echo "  make collectstatic           Coleta arquivos estáticos"
	@echo ""
	@echo "Qualidade de código:"
	@echo "  make lint                    Verifica o código com Ruff"
	@echo "  make lint-fix                Corrige lint automaticamente"
	@echo "  make format                  Formata o código com Ruff"
	@echo "  make format-check            Verifica a formatação"
	@echo "  make quality                 Executa lint e verificação de formatação"
	@echo ""
	@echo "Python:"
	@echo "  make python                  Lista versões de Python disponíveis"
	@echo "  make python-install version=3.15  Instala uma versão do Python"
	@echo "  make python-pin version=3.15      Define a versão do projeto"
	@echo ""
	@echo "Docker Compose (PostgreSQL local):"
	@echo "  make up                      Inicia o PostgreSQL (atalho para db-up)"
	@echo "  make down                    Para o PostgreSQL (preserva o banco)"
	@echo "  make restart                 Reinicia o PostgreSQL"
	@echo "  make logs                    Acompanha os logs do PostgreSQL"
	@echo "  make db-up                   Inicia apenas o PostgreSQL"
	@echo "  make db-down                 Para apenas o PostgreSQL"
	@echo "  make db-shell                Abre o psql no PostgreSQL local"
	@echo ""
	@echo "Deploy:"
	@echo "  make deploy-check            Sincroniza pelo lockfile e verifica deploy"

# ============================================================================
# Ambiente e dependências
# ============================================================================

sync:
	uv sync --locked --all-groups

lock:
	uv lock

upgrade:
	uv lock --upgrade
	uv sync --locked --all-groups

tree:
	uv tree

add:
	@test -n "$(package)" || (echo "Uso: make add package=NOME" && exit 2)
	uv add "$(package)"

add-dev:
	@test -n "$(package)" || (echo "Uso: make add-dev package=NOME" && exit 2)
	uv add --dev "$(package)"

remove:
	@test -n "$(package)" || (echo "Uso: make remove package=NOME" && exit 2)
	uv remove "$(package)"

# ============================================================================
# Django e testes — execução local via uv
# ============================================================================

dev:
	$(UV_ENV) uv run --locked python manage.py runserver 127.0.0.1:8000

dev-base:
	$(UV_ENV) uv run --locked python manage.py runserver 0.0.0.0:8000

check-django:
	$(UV_ENV) uv run --locked python manage.py check

createsuperuser:
	$(UV_ENV) uv run --locked python manage.py createsuperuser

makemigrations:
	$(UV_ENV) uv run --locked python manage.py makemigrations

migrate:
	$(UV_ENV) uv run --locked python manage.py migrate

migrations: makemigrations migrate

shell:
	$(UV_ENV) uv run --locked python manage.py shell

test:
	$(UV_ENV) uv run --locked pytest

test-cov:
	$(UV_ENV) uv run --locked pytest --cov=config --cov=core --cov-report=term-missing

collectstatic:
	$(UV_ENV) uv run --locked python manage.py collectstatic --noinput

# ============================================================================
# Ruff
# ============================================================================

lint:
	uv run --locked ruff check .

lint-fix:
	uv run --locked ruff check --fix .

format:
	uv run --locked ruff format .

format-check:
	uv run --locked ruff format --check .

quality: lint format-check

# ============================================================================
# Python
# ============================================================================

python:
	uv python list

python-install:
	@test -n "$(version)" || (echo "Uso: make python-install version=3.15" && exit 2)
	uv python install "$(version)"

python-pin:
	@test -n "$(version)" || (echo "Uso: make python-pin version=3.15" && exit 2)
	uv python pin "$(version)"

# ============================================================================
# Docker Compose — ambiente local conteinerizado
# ============================================================================

up: db-up

down:
	docker compose stop db

restart:
	docker compose restart db

logs:
	docker compose logs -f --tail=100 db

db-up:
	docker compose up -d --wait db

db-down:
	docker compose stop db

db-shell:
	docker compose exec db sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

# ============================================================================
# Deploy
# ============================================================================

deploy-check:
	uv sync --locked --all-groups
	$(UV_ENV) uv run --locked python manage.py check --deploy
