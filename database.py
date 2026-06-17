from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use the /home/site/wwwroot path for Azure persistence
# Fallback to local ./app.db for local development
AZURE_PATH = "/home/site/wwwroot/app.db"
LOCAL_PATH = "./app.db"

# Use the Azure path if it exists, otherwise use local
DB_FILE = AZURE_PATH if os.path.exists("/home/site/wwwroot") else LOCAL_PATH
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

# connect_args is needed only for SQLite to allow multi-threading
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()