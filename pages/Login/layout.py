from flask import Flask, request, session
from dash  import Input, Output,callback,State,callback_context
from dash import  html, dcc
import dash
import dash_bootstrap_components as dbc
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

dash.register_page(__name__, path='/login')


layout = html.Div(
 
    dbc.Container(
        [
                dbc.Row([
        dbc.Col(html.Div([
             html.H6("Product And Knowledg Unit",className="p-3")
        ]),xs=12, md=8,style={'backgroundColor': 'blue','color':'white','padding':'5px','width':'100%','padding':'0px','height':'50px'})  # Centered navigation bar with offset
    ]),
            dbc.Row(
                dbc.Col(
                    html.Div(
                        [
                            html.H6("Login", className="mb-3"),
                            dcc.Location(id='url_login', refresh=True), 
                            dbc.Input(id='username-box', placeholder='Username', type='text', className="mb-3"),
                            dbc.Input(id='password-box', placeholder='Password', type='password', className="mb-3"),
                            dbc.Button('Login', id='login-button', n_clicks=0, className="d-flex justify-content-end"),
                            html.Div(id='Login-status',style={'color':'red'})  # Add this line to display update status
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

@callback([Output('url_login', 'pathname'),Output('Login-status', 'children')],
              [Input('login-button', 'n_clicks')],
              [State('username-box', 'value'), State('password-box', 'value')])
def successful_login(n_clicks, username, password):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    conn = None 
    if triggered_id == 'login-button' and n_clicks > 0 :
          # Define your connection string (adjust the parameters according to your environment)
        DRIVER = os.getenv('DRIVER')
        SERVER = os.getenv('SERVER')
        DATABASE = os.getenv('DATABASE')
        USERNAME = os.getenv('USER')
        PASSWORD = os.getenv('PASS')

        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

        try:
            # Establish a connection to the database
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Replace 'Users' with your actual table name and columns as per your database schema
            query = "SELECT * FROM Users WHERE username = ? AND password = ?"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                session['authenticated'] = True
                session['username'] = username
                return '/home', ''
            else:
                return "/login", 'Incorrect username or password. Please try again.'

        except pyodbc.Error as e:
            print("Database connection error or query execution error", e)
            return "/login", "Database connection error or query execution error."

        finally:
            if conn:
                conn.close()
    else:
        pass

    return '/login', ''


