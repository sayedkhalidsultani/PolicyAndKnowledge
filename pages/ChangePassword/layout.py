import dash
from dash import html, dcc, callback, Input, Output,State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from db_utils import execute_query
from db_utils import execute_update
from flask import session


dash.register_page(__name__, path='/changepassword')

def update_password(username, password):
    try:
        # Check if the user exists
        user_query = "SELECT * FROM Users WHERE username = %s"
        df_user = execute_query(user_query, (username,))

        if not df_user.empty:
            # Update the password
            update_query = "UPDATE Users SET password = %s WHERE username = %s"
            success, message = execute_update(update_query, (password, username))
            return success, message
        else:
            return False, "User not found."
    except Exception as e:
        print(f"Error updating password: {e}")
        return False, "An error occurred while updating the password."




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