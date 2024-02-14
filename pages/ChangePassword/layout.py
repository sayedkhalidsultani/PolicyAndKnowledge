from flask import Flask, request, session
from dash  import Input, Output,callback,State,callback_context
from dash import  html, dcc
import dash
import dash_bootstrap_components as dbc
import os 
import pyodbc
from dotenv import load_dotenv

load_dotenv()

dash.register_page(__name__, path='/changepassword')

def update_password(username, password):


   # Connection parameters
    DRIVER = os.getenv('DRIVER')
    SERVER = os.getenv('SERVER')
    DATABASE = os.getenv('DATABASE')
    USERNAME = os.getenv('USER')
    PASSWORD = os.getenv('PASS')

    # Hash the password (highly recommended) - Example using bcrypt (ensure bcrypt is installed)
    # import bcrypt
    # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
    conn=None
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Check if the user exists
        user_query = "SELECT * FROM Users WHERE username = ?"
        cursor.execute(user_query, username)
        user = cursor.fetchone()

        if user:
            # Update the password (assuming you have a 'password' column in your 'Users' table)
            update_query = "UPDATE Users SET password = ? WHERE username = ?"
            
            # Use hashed_password instead of password if you're hashing the password
            cursor.execute(update_query, password, username) 
            conn.commit()

            return True, "Password updated successfully."
        else:
            return False, "User not found."
    except pyodbc.Error as e:
        print("Database connection error or query execution error", e)
        return False, "Database connection error or query execution error."
    finally:
        if conn:
            conn.close()




layout = html.Div(
    dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.Div(
                        [
                            html.H6("Change Password", className="mb-3"),
                            dbc.Input(id='password-box', placeholder='NewPassword', type='password', className="mb-3"),
                            dbc.Button('Save', id='Save-button', n_clicks=0, className="d-flex justify-content-end"),
                            html.Div(id='password-update-status')  # Add this line to display update status
                        ],
                        style={'maxWidth': '300px', 'margin': '0 auto'}  # Center the div
                    ),
                    width=12,style={
                            'maxWidth': '300px',
                            'margin': '0 auto',
                            'border': '1px solid #ccc',  # Add border to the div
                            'padding': '20px',  # Add some padding inside the div for aesthetics
                            'borderRadius': '5px',  # Optional: Adds rounded corners to the div
                        },
                ),
                justify="center",
                align="center",
                className="h-100"
            )
        ],
        fluid=True,
        style={'height': '100vh','padding':'0px'}  # Make the container fill the height of the screen
    )
)

@callback(
    Output('password-update-status', 'children'),
    Input('Save-button', 'n_clicks'),
    State('password-box', 'value'),
    prevent_initial_call=True
)
def on_save_button_click(n_clicks, new_password):
    if not new_password:
        return "Please enter a new password."
    
  
    
    # Assume user_id is securely obtained, e.g., from the session
    username = session['username']

    if username:
      success, message = update_password(username=username, password=new_password)
      return message