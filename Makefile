SHELL := /bin/bash

BACKEND_DIR := backend
FRONTEND_DIR := frontend
DEV_DIR := .dev
ROOT_DIR := $(CURDIR)

BACKEND_LOG := $(ROOT_DIR)/$(DEV_DIR)/backend.log
FRONTEND_LOG := $(ROOT_DIR)/$(DEV_DIR)/frontend.log
BACKEND_PID := $(ROOT_DIR)/$(DEV_DIR)/backend.pid
FRONTEND_PID := $(ROOT_DIR)/$(DEV_DIR)/frontend.pid

.PHONY: help dev dev-up dev-down dev-check dev-logs backend frontend

help:
	@echo "Targets:"
	@echo "  dev        Start + check + open UI"
	@echo "  dev-up     Start backend+frontend in background"
	@echo "  dev-down   Stop background backend+frontend"
	@echo "  dev-check  Verify health + auth + frontend"
	@echo "  dev-logs   Tail backend/frontend logs"
	@echo "  backend    Run backend in foreground (reload)"
	@echo "  frontend   Run frontend in foreground"

dev:
	@$(MAKE) dev-up
	@sleep 2
	@$(MAKE) dev-check
	@echo "Open: http://127.0.0.1:5173"
	@command -v open >/dev/null 2>&1 && open http://127.0.0.1:5173 || true

$(DEV_DIR):
	@mkdir -p $(DEV_DIR)

backend:
	cd $(BACKEND_DIR) && \
		. .venv/bin/activate && \
		PYTHONPATH=. alembic upgrade head && \
		uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	cd $(FRONTEND_DIR) && npm run dev

dev-up: $(DEV_DIR)
	@echo "Starting backend (http://127.0.0.1:8000)";
	@cd $(BACKEND_DIR) && \
		mkdir -p "$(ROOT_DIR)/$(DEV_DIR)" && \
		. .venv/bin/activate && \
		PYTHONPATH=. alembic upgrade head && \
		nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 > "$(BACKEND_LOG)" 2>&1 & echo $$! > "$(BACKEND_PID)"
	@echo "Starting frontend (http://127.0.0.1:5173)";
	@cd $(FRONTEND_DIR) && \
		mkdir -p "$(ROOT_DIR)/$(DEV_DIR)" && \
		nohup npm run dev -- --host 127.0.0.1 --port 5173 > "$(FRONTEND_LOG)" 2>&1 & echo $$! > "$(FRONTEND_PID)"
	@echo "PIDs: backend=$$(cat "$(BACKEND_PID)" 2>/dev/null || true) frontend=$$(cat "$(FRONTEND_PID)" 2>/dev/null || true)"

# Stop processes if pid files exist

dev-down:
	@set -e; \
	if [ -f "$(FRONTEND_PID)" ]; then \
		PID=$$(cat "$(FRONTEND_PID)"); echo "Stopping frontend $$PID"; kill $$PID || true; rm -f "$(FRONTEND_PID)"; \
	fi; \
	if [ -f "$(BACKEND_PID)" ]; then \
		PID=$$(cat "$(BACKEND_PID)"); echo "Stopping backend $$PID"; kill $$PID || true; rm -f "$(BACKEND_PID)"; \
	fi

# Quick sanity checks

dev-check:
	@echo "Backend health:"; curl -fsS http://127.0.0.1:8000/healthz | cat; echo
	@echo "Backend OpenAPI:"; curl -fsS http://127.0.0.1:8000/api/v1/openapi.json >/dev/null && echo "ok"
	@echo "Auth login:"; curl -fsS -X POST -d 'username=analyst&password=analyst123' http://127.0.0.1:8000/api/v1/auth/login | cat; echo
	@echo "Frontend:"; curl -fsS http://127.0.0.1:5173/ >/dev/null && echo "ok"

# Tail logs (useful when something fails)

dev-logs:
	@echo "== backend.log =="; tail -n 60 "$(BACKEND_LOG)" 2>/dev/null || true
	@echo "== frontend.log =="; tail -n 60 "$(FRONTEND_LOG)" 2>/dev/null || true
