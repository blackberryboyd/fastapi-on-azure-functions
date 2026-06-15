from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Replace with your Azure SQL Server connection string
SQLALCHEMY_DATABASE_URL = "mssql+pyodbc://sql-server1-off-ice.database.windows.net:1433/database=db1;Driver={ODBC Driver 17 for SQL Server};"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a database session in your routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()