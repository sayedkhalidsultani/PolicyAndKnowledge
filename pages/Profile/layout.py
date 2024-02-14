from dash import Dash, html, dcc
import dash 

dash.register_page(__name__, path='/profile')

    
layout = html.Div([
    dcc.Link(f"ChangePassword", href="/changepassword"),
    # More components for Page 1
])

