# db_utils.py
import os
import pyodbc
import pandas as pd

def load_env():
    # Make sure to change this path when you upload it to GitHub.
    os.getenv('DRIVER')
    os.getenv('SERVER')
    os.getenv('DATABASE')
    os.getenv('USER')
    os.getenv('PASS')

def get_connection_string():
    DRIVER = os.getenv('DRIVER')
    SERVER = os.getenv('SERVER')
    DATABASE = os.getenv('DATABASE')
    USERNAME = os.getenv('USER')
    PASSWORD = os.getenv('PASS')
    return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

def execute_query(SQL_QUERY):
    connectionString = get_connection_string()
    connection = None
    try:
        connection = pyodbc.connect(connectionString)
        cursor = connection.cursor()
        cursor.execute(SQL_QUERY)
        rows = cursor.fetchall()
        df = pd.DataFrame([tuple(row) for row in rows], columns=[column[0] for column in cursor.description])
        return df
    except pyodbc.Error as e:
        print(f"Database error: {e}")
        # Optionally, you can re-raise the exception after logging it or handling it
        # raise e
    finally:
        # The finally block ensures that these cleanup actions are executed
        if connection:
            connection.close()
