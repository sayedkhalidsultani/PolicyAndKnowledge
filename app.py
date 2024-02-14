import dash
from dash import Dash, html, dcc,callback,Input,Output
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os
from flask import Flask,session
from dash.exceptions import PreventUpdate
import os
from dotenv import load_dotenv

load_dotenv()
server = Flask(__name__)
server.secret_key= os.getenv('SECRET_KEY')
app = Dash(__name__,server=server,use_pages=True,external_stylesheets=[dbc.themes.BOOTSTRAP],suppress_callback_exceptions=True)
server = app.server

app.layout=dcc.Loading(
            id="loading-map",
            type="default",  # You can choose the loader style
            children=[dbc.Container(fluid=True, style={'backgroundColor': 'silver','minHeight':'100vh'}, children=[
    # Navigation bar centered within an 8-column width with 2 columns offset using className
    dbc.Row([
        dbc.Col(html.Div([
            dcc.Location(id='url_login_Main', refresh=True),
            html.Div(id='dynamic-nav'),
        ]),xs=12, md=8, className="offset-md-2",style={'backgroundColor': 'white','margin-top':'10px','padding':'0px'})  # Centered navigation bar with offset
    ]),
    # Body content centered within an 8-column width with 2 columns offset using className
    dbc.Row([
        dbc.Col(dash.page_container ,xs=12,md=8, className="offset-md-2", style={'backgroundColor': 'white'})  # Centered body content with offset
    ])
])])

@callback([Output('url_login_Main', 'pathname'),Output('dynamic-nav', 'children')],
          [Input('url_login_Main', 'pathname')])
def redirect_to_login(pathname):
    if session.get('authenticated'):
        # Navigation for authenticated users
        nav = dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/home")),
                dbc.NavItem(dbc.NavLink("Report", href="/pandk")),
                dbc.NavItem(dbc.NavLink("Profile", href="/profile")),
                dbc.NavItem(dbc.NavLink("Logout", href="/logout")),
            ],
            brand="Product And Knowledge Unit",
            brand_href="/",
            color="primary",
            dark=True,
        )
           # Only redirect to /home if the trigger was from logging in
        if pathname == "/login" and trigger_id == 'url_login_Main':
            return "/home", nav
        else:
            # Prevent update to the pathname if already authenticated,
            # allowing navigation to other pages
            return dash.no_update, nav
    else:
        # Navigation for unauthenticated users
        nav = dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Login", href="/login"))
            ],
            brand="Product And Knowledge Unit",
            brand_href="/",
            color="primary",
            dark=True,
        )
        # Public or login page content
         # Redirect to the login page if not authenticated,
        # but only if not already on the login page to avoid infinite redirects
        if pathname != "/login":
            return "/login", nav
        else:
            raise PreventUpdate

    return pathname, nav


if __name__ == '__main__':
    app.run_server(debug=True)