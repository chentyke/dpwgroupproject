.PHONY: api web api-install web-install typegen

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

