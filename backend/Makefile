env_path=../.env

install:
	poetry install

test:
	poetry run pytest -s

run:
	poetry run dotenv -f "$(env_path)" run uvicorn api.main:app

lint:
	poetry run pre-commit run --all-files

db-upgrade:
	poetry run dotenv -f "$(env_path)" run alembic upgrade head

db-downgrade:
	poetry run dotenv -f "$(env_path)" run alembic downgrade -1

db-revision:
	poetry run dotenv -f "$(env_path)" run alembic revision --autogenerate -m "$(name)"

seed:
	curl -X PUT 'http://localhost:8000/seed' -H 'accept: application/json'

download-switzerland-osm:
	wget -O "data/switzerland.gpkg.zip" "https://download.geofabrik.de/europe/switzerland-latest-free.gpkg.zip"
	unzip "data/switzerland.gpkg.zip" -d data/switzerland

download-france-osm:
	wget -O data/franche-comte.gpkg.zip "https://download.geofabrik.de/europe/france/franche-comte-latest-free.gpkg.zip"
	unzip data/franche-comte.gpkg.zip -d data/franche-comte
	wget -O data/rhone-alpes.gpkg.zip "https://download.geofabrik.de/europe/france/rhone-alpes-latest-free.gpkg.zip"
	unzip data/rhone-alpes.gpkg.zip -d data/rhone-alpes

generate-boundaries:
	poetry run python scripts/create_administrative_areas.py
