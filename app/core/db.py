from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings

engine = create_engine(str(settings.DATABASE_URI))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# this is mainly for development purposes, cause I run fastapi locally in development and celery runs in a docker container
celery_engine = create_engine(str(settings.CELERY_DATABASE_URI))
CelerySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=celery_engine)
