from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

from .config import DATABASE_URL

sqlite_url = DATABASE_URL
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
