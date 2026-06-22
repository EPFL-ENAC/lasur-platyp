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

download-world-boundaries:
	wget -O "data/geoBoundariesCGAZ_ADM0.gpkg" "https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/CGAZ/geoBoundariesCGAZ_ADM0.gpkg"

download-nuts-data:
	wget -O "data/NUTS_RG_01M_2024_3035.gpkg" "https://gisco-services.ec.europa.eu/distribution/v2/nuts/gpkg/NUTS_RG_01M_2024_3035.gpkg"
	wget -O "data/NUTS_RG_01M_2021_3035.gpkg" "https://gisco-services.ec.europa.eu/distribution/v2/nuts/gpkg/NUTS_RG_01M_2021_3035.gpkg"
	wget -O "data/LAU_RG_01M_2024_3035.gpkg" "https://gisco-services.ec.europa.eu/distribution/v2/lau/gpkg/LAU_RG_01M_2024_3035.gpkg"

download-switzerland-osm:
	wget -O "data/switzerland/switzerland.gpkg.zip" "https://download.geofabrik.de/europe/switzerland-latest-free.gpkg.zip"
	unzip "data/switzerland/switzerland.gpkg.zip" -d data/switzerland/switzerland

download-france-osm:
	wget -O data/france/franche-comte.gpkg.zip "https://download.geofabrik.de/europe/france/franche-comte-latest-free.gpkg.zip"
	unzip data/france/franche-comte.gpkg.zip -d data/france/franche-comte
	wget -O data/france/rhone-alpes.gpkg.zip "https://download.geofabrik.de/europe/france/rhone-alpes-latest-free.gpkg.zip"
	unzip data/france/rhone-alpes.gpkg.zip -d data/france/rhone-alpes

generate-filtering-boundaries:
	poetry run python scripts/create_filtering_boundaries.py

generate-multilevel-boundaries:
	poetry run python scripts/create_multilevel_boundaries.py
