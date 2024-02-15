import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash.dash_table import DataTable
import requests
import pyodbc
from db_utils import execute_query

dash.register_page(__name__,path='/pandk/maps')

SQL_QUERY = "SELECT Indicator, Xcolumns, FirstColumnHeader, SubHeader, Colors, Year, [Values], ChartType, Source, xSecondary, SortOrder, ISPivot, Lat, Lon, Unit, Category, ValueType, YaxisTitle FROM Results where ChartType  IN ('Map','MapPoint')"

color_palette = [
    "#9ecae1",
    "#41ab5d",
    "#edf8b1",
    "#ef8a62",
    "#7fcdbb",
    "#d1e5f0",
    "#67a9cf",
    "#34495E",
    "#00A08B",
    "#A777F1",
    "#565656",
    "#778AAE",
    "#ec7014",
    "#c6dbef",
     "#08306b",
]


# Loading Data

# Map Data is Displayed Here




layout = html.Div(
    [
    
                dbc.Container(
                    [
                        dbc.Row(
                            dbc.Col(
                                [
                                    dcc.Dropdown(
                                        id="category-dropdown-Map",
                                        
                                        style={'marginBottom': '10px'}
                                                        ),
                                    html.Div(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        html.Div(id="charts-ouput-Map"),
                                                        width=12,
                                                    )
                                                ]
                                            )
                                        ],
                                        id="charts-container",
                                    ),
                                ],
                                width=12,
                            ),
                            justify="center",
                            style={'marginTop':'10px'}
                        ),
                    ],
                   
                ),
           
    ],
)


# Define the callback to update the bar charts
@callback([Output("category-dropdown-Map", "options"),
          Output("charts-ouput-Map", "children")], 
          [Input("category-dropdown-Map", "value")])
def update_bar_charts(selected_category):
    # Filter the DataFrame based on selected category
    df = execute_query(SQL_QUERY)
    #dropdown_options = [{"label": category, "value": category} for category in df["Category"].unique()]
     # Set dropdown options based on the fetched data
    dropdown_options = [
        {"label": str(category), "value": str(category)}
        for category in df["Category"].dropna().unique()
    ]
    
    # # # Set default value for dropdown if not already selected or if selected category is not in options
    # if not selected_category or selected_category not in df["Category"].dropna().unique():
    #     selected_category = df["Category"].dropna().unique()[0] if not df.empty else "Please Select"
 
        
    filtered_df = df[df["Category"] == selected_category].copy()
    fig = {}
    # Fetch and load the GeoJSON data
    geojson_url = "https://raw.githubusercontent.com/sayedkhalidsultani/ShapFiles/main/Province.json"
    geojson_response = requests.get(geojson_url)
    geojson = geojson_response.json()

    # Mapping Starts Here
    def categorize_value(value):
        if value <= step:
            return "0-{}".format(step)
        elif value <= 2 * step:
            return "{}-{}".format(step, 2 * step)
        elif value <= 3 * step:
            return "{}-{}".format(2 * step, 3 * step)
        else:
            return ">{}".format(3 * step)

    filtered_df.sort_values(by=["SortOrder", "Indicator"], inplace=True)

    # Ensure 'Colors' is treated as categorical data for grouping
    filtered_df["Colors"] = filtered_df["Colors"].astype(str)

    indicators = filtered_df["Indicator"].unique()

    # Create a bar chart for each indicator
    charts = []

    # Check for secondary

    for indicator in indicators:
        tables = []
        indicator_df = filtered_df[filtered_df["Indicator"] == indicator]

        # Maps

        max_value = indicator_df["Values"].max()
        step = (max_value // 3) + 1
        color_map = {
            "0-{}".format(step): "#e34a33",
            "{}-{}".format(step, 2 * step): "#fdbb84",
            "{}-{}".format(2 * step, 3 * step): "#fee08b",
            ">{}".format(3 * step): "#31a354",
        }

        indicator_df["MapCategory"] = indicator_df["Values"].apply(categorize_value)

        indicator_df["SortOrder"] = indicator_df["SortOrder"].fillna(0.0)

        indicator_df["SortOrder"] = pd.to_numeric(
            indicator_df["SortOrder"], errors="coerce"
        )
        indicator_df.sort_values(by=["SortOrder", "Indicator"], inplace=True)

        chart_type = indicator_df["ChartType"].iloc[0]

        yaxis_title = indicator_df["YaxisTitle"].iloc[0]
        if pd.isna(yaxis_title):
            yaxis_title = ""
        # Get Percentage
        value_type = indicator_df["ValueType"].iloc[0]  # Extracting the ValueType
        # Check for secondary chart requirement
        secondary_df = indicator_df[indicator_df["xSecondary"].notnull()]
        xsecondary = indicator_df["xSecondary"].iloc[0]
        isPivot = indicator_df["ISPivot"].iloc[0]
        if chart_type == "Map":
                MapYear = indicator_df["Year"].iloc[0]

                fig = create_choropleth_map(indicator_df, geojson, color_map, MapYear)
                graph_with_border = html.Div(
                    dcc.Graph(figure=fig),
                    style={
                        "border": "1px solid silver",  # Adding a 1px solid border
                        "padding": "10px",
                        "margin-top": "10px",
                        "margin-bottom": "10px",  # Optional: Adds space between charts
                    },
                )
                charts.append(graph_with_border) 
            
        elif chart_type=='MapPoint':
                # Assuming 'Colors' column contains categorical data
                 unique_categories = indicator_df['Colors'].unique()
                 category_color_map = {category: color for category, color in zip(unique_categories, color_palette)}

                    # Map each category to a color
                 indicator_df['ColorMapped'] = indicator_df['Colors'].map(category_color_map)

                 traces = []
               
                 for category in unique_categories:
                    df_filtered = indicator_df[indicator_df['Colors'] == category]
                    traces.append(go.Scattermapbox(
                        lat=df_filtered['Lat'],
                        lon=df_filtered['Lon'],
                        mode='markers',
                        marker=go.scattermapbox.Marker(color=category_color_map[category]),
                        name=category,  # This sets the legend entry
                       

                    ))

                # Create the figure with all traces
                 fig = go.Figure(traces)
                 
                 fig.update_layout(mapbox_style="carto-positron",
                  height=750,  # Height in pixels
              
                  
                  mapbox=dict(
                    center={"lat": 34.634817, "lon": 66.342506},  # Center of the map
                    zoom=5  # Zoom level
                ),
                    title={
                        "text":indicator,
                        "y": 0.9,
                        "x": 0.5,
                        "xanchor": "center",
                        "yanchor": "top",
                        "font": {"size": 14},
                    },legend=dict(
      
                    title="",
                ))
                 graph_with_border = html.Div(
                    dcc.Graph(figure=fig),
                    style={
                        "border": "1px solid silver",  # Adding a 1px solid border
                        "padding": "10px",
                        "margin-top": "10px",
                        "margin-bottom": "10px",  # Optional: Adds space between charts
                    },
                 )
                 charts.append(graph_with_border) 
            # Append the figure wrapped in a dcc.Graph component to the list of charts
     
    return dropdown_options,charts

# Function to create the choropleth map figure
def create_choropleth_map(df, geojson, color_discrete_map, selected_year=None):
    df["Province"] = df["Xcolumns"]
    Indicator = df["Indicator"].iloc[0]
    unique_categories = df['MapCategory'].unique()
    
    if selected_year is not None:
        df = df[df["Year"] == selected_year]
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        color="MapCategory",
        locations="Province",
        featureidkey="properties.Province",
        center={"lat": 34.634817, "lon": 66.342506},
        mapbox_style="white-bg",
        zoom=5,
        color_discrete_map={category: color for category, color in zip(unique_categories, color_palette)},
        height=920,
        hover_data={"Values": True},
    )

    fig.update_layout(
        dragmode=False,
        legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="bottom",
            y=-0.5,  # Moves the legend below the chart
            xanchor="center",
            x=0.5,  # Centers the legend
            title="",
        ),
        title={
            "text": Indicator,
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 14},
        },
        title_font=dict(size=14),
    )

    return fig
