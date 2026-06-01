from fastapi import FastAPI

from app.core.db import engine
from app.core.settings import settings
from app.models import Base
from app.routers import auth, users

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    # docs_url="/docs",  # default
    # redoc_url="/redoc", # default
)

# Base.metadata.create_all(engine)

app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)
