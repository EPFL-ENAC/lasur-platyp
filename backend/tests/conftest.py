import os

# dummy settings so that api.config loads without a .env (no service is contacted in tests)
os.environ.setdefault("DB_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("KEYCLOAK_API_ID", "test-api")
os.environ.setdefault("KEYCLOAK_API_SECRET", "test")
