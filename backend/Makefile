env_path=../.env
count ?= 10

install:
	uv sync

test:
	uv run pytest -s

run:
	uv run dotenv -f "$(env_path)" run uvicorn api.main:app

lint:
	uv run pre-commit run --all-files

db-upgrade:
	uv run dotenv -f "$(env_path)" run alembic upgrade head

db-downgrade:
	uv run dotenv -f "$(env_path)" run alembic downgrade -1

db-revision:
	uv run dotenv -f "$(env_path)" run alembic revision --autogenerate -m "$(name)"

seed:
	uv run dotenv -f "$(env_path)" run python scripts/seed_records.py --campaign-id $(campaign_id) --count $(count)

#
# Maps
#

# Download original maps data from various sources and store them in the data folder. 
# This is a prerequisite for generating boundaries and pmtiles.
download-data: download-world-boundaries download-nuts-data download-switzerland-osm download-france-osm

download-world-boundaries:
	mkdir -p data
	wget -O "data/geoBoundariesCGAZ_ADM0.gpkg" "https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/CGAZ/geoBoundariesCGAZ_ADM0.gpkg"

download-nuts-data:
	mkdir -p data
	wget -O "data/NUTS_RG_01M_2024_3035.gpkg" "https://gisco-services.ec.europa.eu/distribution/v2/nuts/gpkg/NUTS_RG_01M_2024_3035.gpkg"
	wget -O "data/NUTS_RG_01M_2021_3035.gpkg" "https://gisco-services.ec.europa.eu/distribution/v2/nuts/gpkg/NUTS_RG_01M_2021_3035.gpkg"
	wget -O "data/LAU_RG_01M_2024_3035.gpkg" "https://gisco-services.ec.europa.eu/distribution/v2/lau/gpkg/LAU_RG_01M_2024_3035.gpkg"

download-switzerland-osm:
	mkdir -p data/switzerland
	wget -O "data/switzerland/switzerland.gpkg.zip" "https://download.geofabrik.de/europe/switzerland-latest-free.gpkg.zip"
	unzip "data/switzerland/switzerland.gpkg.zip" -d data/switzerland/switzerland

download-france-osm:
	mkdir -p data/france
	wget -O data/france/franche-comte.gpkg.zip "https://download.geofabrik.de/europe/france/franche-comte-latest-free.gpkg.zip"
	unzip data/france/franche-comte.gpkg.zip -d data/france/franche-comte
	wget -O data/france/rhone-alpes.gpkg.zip "https://download.geofabrik.de/europe/france/rhone-alpes-latest-free.gpkg.zip"
	unzip data/france/rhone-alpes.gpkg.zip -d data/france/rhone-alpes

# Generate boundaries from the downloaded data. 
# This is a prerequisite for generating pmtiles.
generate-boundaries: generate-filtering-boundaries generate-multilevel-boundaries

generate-filtering-boundaries:
	uv run python scripts/create_filtering_boundaries.py

generate-multilevel-boundaries:
	uv run python scripts/create_multilevel_boundaries.py

pmtiles:
	for f in data/*.geojson; do \
		base=$$(basename $$f .geojson); \
		tippecanoe -zg -o data/$$base.pmtiles --drop-densest-as-needed --extend-zooms-if-still-dropping --force $$f; \
	done

pmtiles2:
	tippecanoe -Z 1  -z 5  -o data/national_boundaries.pmtiles --drop-densest-as-needed --extend-zooms-if-still-dropping --force data/national_boundaries.geojson
	tippecanoe -Z 5  -z 10 -o data/regional_boundaries.pmtiles --drop-densest-as-needed --extend-zooms-if-still-dropping --force data/regional_boundaries.geojson
	tippecanoe -Z 10 -z 12 -o data/filtering_boundaries.pmtiles --drop-densest-as-needed --extend-zooms-if-still-dropping --force data/filtering_boundaries.geojson
	tippecanoe -Z 12       -o data/local_boundaries.pmtiles --drop-densest-as-needed --extend-zooms-if-still-dropping --force data/local_boundaries.geojson

# Upload the generated pmtiles to the S3 bucket.
version=$(shell date +%FT%H:%M)
bucket=10208-fcd9acb029f419e6493edf97f4592b96
folder=platyp

cdn-maps:
	for f in data/*.pmtiles; do \
		s3cmd put --acl-public --guess-mime-type $$f s3://${bucket}/${folder}/maps/${version}/$$f; \
	done
	@echo "Uploaded pmtiles to CDN in folder: ${folder}/maps/${version}"

sync:
	s3cmd sync s3://${bucket}/${folder}/maps/${version}/ maps-${version}/
