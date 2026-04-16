from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings

engine = create_engine(str(settings.DATABASE_URI))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
