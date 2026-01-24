.PHONY: help venv install migrate revision upgrade downgrade stamp-current

help:
	@echo "Targets:"
	@echo "  install        Install backend deps into current venv"
	@echo "  migrate        Apply migrations (upgrade head)"
	@echo "  revision MSG=...  Create autogen migration (requires MSG)"
	@echo "  upgrade        Same as migrate"
	@echo "  downgrade      Downgrade one revision"
	@echo "  stamp-current  Mark DB as at current head without running migrations (use carefully)"

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

migrate: upgrade

upgrade:
	PYTHONPATH=. alembic upgrade head

downgrade:
	PYTHONPATH=. alembic downgrade -1

revision:
	@if [ -z "$(MSG)" ]; then echo "MSG is required: make revision MSG='add foo'"; exit 2; fi
	PYTHONPATH=. alembic revision --autogenerate -m "$(MSG)"

stamp-current:
	PYTHONPATH=. alembic stamp head
