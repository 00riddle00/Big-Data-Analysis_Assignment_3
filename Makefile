# vim: set ft=make tw=100 nu noet ts=8 sw=8:
# =============================================================================
# Makefile — AIS MongoDB Sharding Pipeline
# =============================================================================
# Usage: make <target>
# Run `make help` to see all available targets.
# =============================================================================

PYTHON_VERSION := 3.13.13
TIMESTAMP      := $(shell date +%F_%H_%M_%S)

MONGOS         := mongos
WORKER         := worker
SCRIPTS_DIR    := /scripts
DATA_DIR       := /data_arch
CSV_FILE       := $(DATA_DIR)/aisdk-2026-04-18.csv

# Load environment variables from .env file if it exists
ifneq (,$(wildcard .env))
    include .env
    export
endif

.PHONY: help all deps data lint up down init insert filter analyze \
        test clean clean-env distclean

# -----------------------------------------------------------------------------

help:
	@echo ""
	@echo "AIS MongoDB Sharding Pipeline"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  help          Show this help message"
	@echo "  all           Run full pipeline: up + init + insert + filter + analyze"
	@echo "  deps          Install Python dependencies via uv (incremental)"
	@echo "  data          Show instructions for downloading the AIS dataset"
	@echo "  lint          Lint and format Python code (ruff + black)"
	@echo "  up            Start the MongoDB sharded cluster"
	@echo "  down          Stop the MongoDB sharded cluster"
	@echo "  init          Initialize replica sets and enable sharding"
	@echo "  insert        Run parallel CSV insertion (Task 2)"
	@echo "  filter        Run parallel noise filtering (Task 3)"
	@echo "  analyze       Run delta t calculation and histogram generation (Task 4)"
	@echo "  test          Run unit tests"
	@echo "  clean         Remove generated output files"
	@echo "  clean-env     Remove Python virtual environment"
	@echo "  distclean     clean + clean-env + down + remove Docker volumes"
	@echo ""

# -----------------------------------------------------------------------------

all: up init insert filter analyze
	@echo "==> Full pipeline complete."

# -----------------------------------------------------------------------------

# Incremental dependency install using uv.
# Uses a stamp file to avoid unnecessary reinstalls — uv sync only runs
# if uv.lock is newer than .venv/.stamp.
deps: .venv/.stamp

.venv/.stamp: uv.lock
	@echo "==> Installing Python $(PYTHON_VERSION)"
	pyenv install -s $(PYTHON_VERSION)
	pyenv local $(PYTHON_VERSION)
	@echo "==> Creating virtual environment and syncing dependencies"
	uv venv
	uv sync --all-groups
	@date "+%F %T %Z" > $@
	@echo "==> Dependencies installed."

# -----------------------------------------------------------------------------

data:
	@echo ""
	@echo "Download the AIS dataset manually:"
	@echo ""
	@echo "  wget http://aisdata.ais.dk/aisdk-2026-04-18.zip"
	@echo "  unzip aisdk-2026-04-18.zip -d data_arch/"
	@echo ""
	@echo "Or paste the URL directly into your browser address bar."
	@echo "Place the resulting CSV at: data_arch/aisdk-2026-04-18.csv"
	@echo ""

# -----------------------------------------------------------------------------

lint:
	@echo "==> Linting and formatting Python code"
	uv run ruff check . --fix
	uv run ruff check --select I --fix .
	uv run ruff format .
	uv run black --line-length=88 --preview \
		--enable-unstable-feature=string_processing .

# -----------------------------------------------------------------------------

up:
	@echo "==> Starting MongoDB sharded cluster"
	docker compose up -d
	@echo "==> Cluster started. Run 'make init' if this is a fresh start."

down:
	@echo "==> Stopping MongoDB sharded cluster"
	docker compose down

# -----------------------------------------------------------------------------

init:
	@echo "==> Initializing config server replica set"
	docker exec -it $(MONGOS) mongosh --eval \
		"$$(cat scripts/init_configsvr.js)" || true
	@echo "==> Initializing shard1 replica set"
	docker exec -it shard1 mongosh --eval \
		"$$(cat scripts/init_shard1.js)" || true
	@echo "==> Initializing shard2 replica set"
	docker exec -it shard2 mongosh --eval \
		"$$(cat scripts/init_shard2.js)" || true
	@echo "==> Configuring mongos router and enabling sharding"
	docker exec -it $(MONGOS) mongosh --eval \
		"$$(cat scripts/init_mongos.js)" || true
	@echo "==> Cluster initialized."

# -----------------------------------------------------------------------------

insert:
	@echo "==> Running parallel CSV insertion (Task 2)"
	docker exec -it $(WORKER) uv run --project / python insert.py

filter:
	@echo "==> Running parallel noise filtering (Task 3)"
	docker exec -it $(WORKER) uv run --project / python filter.py

analyze:
	@echo "==> Running delta t calculation and histogram generation (Task 4)"
	docker exec -it $(WORKER) uv run --project / python analyze.py

# -----------------------------------------------------------------------------

test:
	@echo "==> No tests defined yet."

# -----------------------------------------------------------------------------

clean:
	@echo "==> Removing generated output files"
	rm -f outputs/*.png outputs/*.mp4
	@echo "==> Done."

clean-env:
	@echo "==> Removing Python virtual environment"
	rm -rf .venv
	@echo "==> Removed .venv."

distclean: clean clean-env down
	@echo "==> Removing Docker volumes"
	docker compose down -v
	@echo "==> distclean complete."
