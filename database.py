import os
from mssql_python import connect

db_test_pw = os.getenv("AZURE_SQL_PASSWORD")
server = os.getenv('AZURE_SQL_SERVER')
port = os.getenv('AZURE_SQL_PORT')
database = os.getenv('AZURE_SQL_DATABASE')

# For user-assigned managed identity.
client_id = os.getenv('AZURE_SQL_USER')
connection_string = f'Server={server},{port};Database={database};UID={client_id};Pwd={db_test_pw};Authentication=ActiveDirectoryMSI;Encrypt=yes;'

conn = connect(connection_string)


# Dependency to get a database session in your routes
def get_db():
    db = conn.cursor()
    try:
        yield db
    finally:
        db.close()