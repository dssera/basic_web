from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

from .config import settings

engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
