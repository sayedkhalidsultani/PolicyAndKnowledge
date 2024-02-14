from dash import html, dcc
from flask import session
import dash




dash.register_page(__name__, path='/logout')

# This could be a simple page showing a logout message and redirecting after a few seconds
layout = html.Div([
    html.H2('You have been logged out.'),
    dcc.Location(id='redirect-after-logout', refresh=True),
    html.P('Redirecting to the login page...'),
])

# Optional: You might add a callback to automatically redirect after a few seconds
@dash.callback(
    dash.Output('redirect-after-logout', 'pathname'),
    dash.Input('redirect-after-logout', 'id'),  # This input is just to trigger the callback
)
def redirect_to_login(_):
    # Clear the session or perform any other cleanup
    session.clear()
    # Redirect to the login page or home page
    return '/login'
