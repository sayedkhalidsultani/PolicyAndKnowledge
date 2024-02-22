import dash
from dash import Dash, html, dcc,callback,Input,Output
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os
from flask import Flask,session
from dash.exceptions import PreventUpdate
from dash import no_update
import os
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
    ]),
])])

@callback([Output('url_login_Main', 'pathname'), Output('dynamic-nav', 'children')],
          [Input('url_login_Main', 'pathname')])
def redirect_to_login(pathname):
    ctx = dash.callback_context

    if not ctx.triggered:
        # On initial load, if no input has triggered the callback, don't update.
        # This prevents an unnecessary redirect on slow connections before session state is checked.
        return no_update, no_update
    elif session.get('authenticated'):
        # Logic for authenticated users remains the same
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
        # Determine if the callback was triggered by a direct navigation to /login
        if pathname == "/login" and ctx.triggered[0]['prop_id'] == 'url_login_Main.pathname':
            return "/home", nav
        return no_update, nav
    else:
        # Logic for unauthenticated users remains the same
        nav = dbc.NavbarSimple(
            children=[dbc.NavItem(dbc.NavLink("Login", href="/login"))],
            brand="Policy And Knowledge Unit",
            brand_href="/login",
            color="primary",
            dark=True,
        )
        if pathname != "/login":
            return "/login", nav
        return no_update, no_update 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
