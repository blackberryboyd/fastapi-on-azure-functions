from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

db_test_pw = os.getenv("AZURE_SQL_PASSWORD")
# Replace with your Azure SQL Server connection string
SQLALCHEMY_DATABASE_URL = "mssql+pyodbc://office-workout.database.windows.net:1433/database=free-sql-db-9896707;adminuser;{db_test_pw};;Encrypt=yes;TrustServerCertificate=no;Driver={ODBC Driver 17 for SQL Server};"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a database session in your routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()