## core
DOCKER_COMPOSE := docker compose -f docker-compose.yml
UV := uv
UVX := $(UV)x

.PHONY: clean-db clean ps build up stop down restart install check format lint typecheck migrate run export logs seed help

clean-db:
	$(DOCKER_COMPOSE) down -v

clean:
	$(DOCKER_COMPOSE) down -v --rmi all

ps:
	$(DOCKER_COMPOSE) ps -a

build:
	COMPOSE_BAKE=true $(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

stop:
	$(DOCKER_COMPOSE) stop

down:
	$(DOCKER_COMPOSE) down

restart:
	make stop
	make build
	make up

logs:
	$(DOCKER_COMPOSE) logs -f

install:
	$(UV) sync --all-groups

check:
	make install
	$(UVX) ruff check --fix
	$(UVX) ruff format --check

format:
	$(UVX) ruff format

lint:
	$(UVX) ruff check

typecheck:
	$(UVX) ty check src/

migrate:
	$(UV) run python -m scripts.migrate

seed:
	$(UV) run python -m scripts.seed

run:
	$(UV) run uvicorn src.main:app --reload --loop uvloop

export:
	$(UV) export --format requirements-txt --output requirements.txt

help:
	@grep -E '^[a-zA-Z_-]+:.*?#' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?#"}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'