# db_utils.py
import os
import pymssql
import pandas as pd
from decouple import config


server="mssql-163420-0.cloudclusters.net:12454"
database=os.getenv('database')
user=os.getenv('user')
password=os.getenv('password')

def execute_query(SQL_QUERY):
    connection = None
    try:
        connection = pymssql.connect(server,user,password,database)
        df = pd.read_sql(SQL_QUERY,connection)
        return df
    except pymssql.Error as e:
        print(f"Database error: {e}")
        # Optionally, you can re-raise the exception after logging it or handling it
        # raise e
    finally:
        # The finally block ensures that these cleanup actions are executed
        if connection:
            connection.close()
