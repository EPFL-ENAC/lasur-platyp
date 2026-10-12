all: run-db

run-db:
	docker compose up -d --pull=always postgres

stop-db:
	docker compose stop postgres

down-db:
	docker compose down postgres

connect-db:
	psql -h localhost -d platyp -U postgres

# Bump app versions: make bump-patch | bump-minor | bump-major
bump-%:
	cd backend && uv version --bump $* --no-sync
	cd admin && npm version $* --no-git-tag-version
	cd collect && npm version $* --no-git-tag-version
