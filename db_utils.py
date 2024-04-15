# db_utils.py
import os
import pymssql
import pandas as pd

from dotenv import load_dotenv

# Make sure this is at the top of your db_utils.py file
load_dotenv()

server=os.getenv('server')
database=os.getenv('database')
user=os.getenv('user')
password=os.getenv('password')

def execute_query(SQL_QUERY,params=None):
    connection = None
    try:
        connection = pymssql.connect(server,user,password,database)
        if params:
            df = pd.read_sql(SQL_QUERY, connection, params=params)
        else:
            df = pd.read_sql(SQL_QUERY, connection)

        return df
    except pymssql.Error as e:
        print(f"Database error: {e}")
        # Optionally, you can re-raise the exception after logging it or handling it
        # raise e
    finally:
        # The finally block ensures that these cleanup actions are executed
        if connection:
            connection.close()

def execute_update(SQL_QUERY, params=None):

    connection = None
    try:
        connection = pymssql.connect(server, user, password, database)
        cursor = connection.cursor()
        
        if params:
            cursor.execute(SQL_QUERY, params)
        else:
            cursor.execute(SQL_QUERY)
        
        connection.commit()  # Commit the changes to the database
        return True, "Operation successful."
    except pymssql.Error as e:
        print(f"Database error: {e}")
        return False, "Database error occurred."
    finally:
        if connection:
            connection.close()