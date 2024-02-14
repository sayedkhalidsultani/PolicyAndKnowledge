from dash import html
import dash

dash.register_page(__name__, path='/home')

layout = html.Div([
     html.P('Welcome to the Home page...'),
    # More components for Page 1
])
