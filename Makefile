all: run-db

run-db:
	docker compose up -d --pull=always postgres

stop-db:
	docker compose stop postgres

down-db:
	docker compose down postgres

connect-db:
	psql -h localhost -d platyp -U postgres
