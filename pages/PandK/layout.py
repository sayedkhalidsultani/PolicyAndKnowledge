from dash import Dash, html, dcc
import dash

dash.register_page(__name__,path='/pandk')

layout = html.Div([
    dcc.Link(f"Indicators", href="/pandk/indicators"),
    html.Br(),
    dcc.Link(f"maps", href="/pandk/maps")
    # More components for Page 1
])
