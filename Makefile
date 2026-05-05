.PHONY: api web api-install web-install typegen etl test-backend

api:
	uvicorn app.main:app --reload

web:
	cd web && npm run dev

api-install:
	python3 -m pip install -r requirements.txt

web-install:
	cd web && npm install

typegen:
	cd web && npm run generate:types

etl:
	python -c "from app.services.data_repository import get_player_repository; print(get_player_repository().run_etl())"

test-backend:
	python -m compileall app tests
	python -m pytest -q tests/test_backend_services.py
