from flask import Flask, request, session
from dash  import Input, Output,callback,State,callback_context
from dash import  html, dcc
import dash
import dash_bootstrap_components as dbc
import pyodbc
import os
from db_utils import execute_query 


dash.register_page(__name__, path='/login')


layout = html.Div(
 
    dbc.Container(
        [
                dbc.Row([
        dbc.Col(html.Div([
             html.H6("Policy And Knowledg Unit",className="p-3")
        ]),xs=12, md=8,style={'backgroundColor': 'blue','color':'white','padding':'5px','width':'100%','padding':'0px','height':'50px'})  # Centered navigation bar with offset
    ]),
            dbc.Row(
                dbc.Col(
                    html.Div(
                        [
                            html.H6("Login", className="mb-3"),
                            dcc.Location(id='url_login', refresh=True), 
                            dbc.Input(id='username-box', placeholder='Username', type='text', className="mb-3",n_submit=0),
                            dbc.Input(id='password-box', placeholder='Password', type='password', className="mb-3",n_submit=0),
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
              [Input('login-button', 'n_clicks'),Input('username-box', 'n_submit'), Input('password-box', 'n_submit')],
              [State('username-box', 'value'), State('password-box', 'value')])
def successful_login(n_clicks,username_submit, password_submit, username, password):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    conn = None 
    if triggered_id in ['login-button', 'username-box', 'password-box'] and (n_clicks > 0 or username_submit > 0 or password_submit > 0) :
        query = "SELECT * FROM Users WHERE username = %s AND password = %s"
        params = (username, password)
        try:
            df = execute_query(query, params)
 
            if not df.empty:
                session['authenticated'] = True
                session['username'] = username
                return 'pandk/indicators', ''
            else:
                return "/login", 'Incorrect username or password. Please try again.'

        except Exception as e:
            print("Database connection error or query execution error", e)
            return "/login", "Database connection error or query execution error."

        finally:
            if conn:
                conn.close()
    else:
        pass

    return '/login', ''


