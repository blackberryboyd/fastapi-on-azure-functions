from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use local ./app.db for development (simpler path handling on Windows)
DB_FILE = "./app.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.abspath(DB_FILE)}"

# Create Base here and export it so models.py can use the same one
Base = declarative_base()

# connect_args is needed only for SQLite to allow multi-threading
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()