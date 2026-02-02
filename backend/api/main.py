from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from api.config import config
from api.db import get_session, AsyncSession
from logging import basicConfig, INFO, DEBUG
from pydantic import BaseModel
from sqlalchemy.sql import text
from api.views.companies import router as companies_router
from api.views.actions import router as actions_router
from api.views.campaigns import router as campaigns_router
from api.views.participants import router as participants_router
from api.views.records import router as records_router
from api.views.users import router as users_router
from api.views.collect import router as collect_router
from api.views.stats import router as stats_router
from api.views.isochrones import router as isochrones_router

basicConfig(level=DEBUG)

# Rate limiting configuration
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(root_path=config.PATH_PREFIX)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@app.get(
    "/healthz",
    tags=["Healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
async def get_health(
    session: AsyncSession = Depends(get_session),
) -> HealthCheck:
    """
    Endpoint to perform a healthcheck on for kubenernetes liveness and
    readiness probes.
    """
    # Check DB connection
    try:
        await session.exec(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {e}")

    return HealthCheck(status="OK")


app.include_router(
    companies_router,
    prefix="/company",
    tags=["Companies"],
)
app.include_router(
    actions_router,
    prefix="/action",
    tags=["Company Actions"],
)
app.include_router(
    campaigns_router,
    prefix="/campaign",
    tags=["Campaigns"],
)
app.include_router(
    participants_router,
    prefix="/participant",
    tags=["Participants"],
)
app.include_router(
    records_router,
    prefix="/record",
    tags=["Records"],
)

app.include_router(
    users_router,
    prefix="/user",
    tags=["Users"],
)

app.include_router(
    collect_router,
    prefix="/collect",
    tags=["Collect"],
)

app.include_router(
    stats_router,
    prefix="/stats",
    tags=["Statistics"],
)

app.include_router(
    isochrones_router,
    prefix="/isochrones",
    tags=["Isochrones"],
)
