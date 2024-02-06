import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash.dash_table import DataTable
import requests
from plotly.subplots import make_subplots
import math

# Sample DataFrame (replace this with your dynamic data source)
# Assuming df is your DataFrame after loading the data from your source

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
# Make sure to change this path when you upload it to github.
excel_file = "https://raw.githubusercontent.com/sayedkhalidsultani/PolicyAndKnowledge/main/Result.csv"
df = pd.read_csv(excel_file)
color_palette = [
    "#b2182b",
    "#ef8a62",
    "#fddbc7",
    "#d1e5f0",
    "#67a9cf",
    "#34495E",
    "#FD3216",
    "#00A08B",
    "#A777F1",
    "#AF0038",
    "#565656",
    "#778AAE",
]


# Function to create the choropleth map figure
def create_choropleth_map(df, geojson, color_discrete_map, selected_year=None):
    df["Province"] = df["Xcolumns"]
    Indicator = df["Indicator"].iloc[0]

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
        color_discrete_map=color_discrete_map,
        height=920,
        hover_data={"Values": True},
    )

    fig.update_layout(
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
        },
        title_font=dict(size=14),
    )

    return fig


app.layout = html.Div(
    [
        dcc.Loading(
            id="loading-map",
            type="default",  # You can choose the loader style
            children=[
                dbc.Container(
                    [
                        dbc.Row(
                            dbc.Col(html.H3("Policy And Knowledge Unit"), width=12),
                            justify="center",
                        ),
                        dbc.Row(
                            dbc.Col(
                                [
                                    dcc.Dropdown(
                                        id="category-dropdown",
                                        options=[
                                            {
                                                "label": str(i) if i else "Default",
                                                "value": str(i) if i else "Default",
                                            }
                                            for i in df["Category"].dropna().unique()
                                        ],
                                        value=str(df["Category"].dropna().unique()[0]),
                                    ),
                                    html.Div(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        html.Div(id="charts-ouput"),
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
                        ),
                        dbc.Row(dbc.Col(html.H6(""), width=12), justify="right"),
                    ],
                    style={
                        "maxWidth": "1024px",
                        "margin": "10px auto",
                        "border": "1px solid silver",
                        "background": "white",
                        "padding-bottom": "20px",
                    },
                ),
            ],
            style={"width": "80%", "margin": "auto", "position": "relative"},
        ),
    ],
    style={
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "space-between",
        "background": "silver",
    },
)


# Define the callback to update the bar charts
@app.callback(Output("charts-ouput", "children"), [Input("category-dropdown", "value")])
def update_bar_charts(selected_category):
    # Filter the DataFrame based on selected category
    filtered_df = df[df["Category"] == selected_category].copy()

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

    # # Get a list of all indicators for the selected category
    # df["Indicator"] = df["Indicator"].str.strip()

    indicators = filtered_df["Indicator"].unique()

    # Create a bar chart for each indicator
    charts = []

    # def truncate_to_two_decimals(x):
    #     # if isinstance(x, float) and not math.isnan(x):
    #     #     return int(x * 100) / 100.0
    #     # else:
    #     #     return x

    #     if isinstance(x, float) and not math.isnan(x):
    #         # Convert to string and split at the decimal point
    #         integer_part, decimal_part = str(x).split(".")
    #         # Truncate the decimal part and reform the number
    #         truncated = f"{integer_part}.{decimal_part[:2]}"
    #         return float(truncated)
    #     else:
    #         # Return the original value if it's not a float
    #         return x

    # df["Values"] = df["Values"].apply(truncate_to_two_decimals)

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
        if not secondary_df.empty:
            if chart_type == "Line":
                LineBasevalues = indicator_df[indicator_df["xSecondary"] == "B"]
                lineSecondaryvalues = indicator_df[indicator_df["xSecondary"] == "L"]
                fig = create_line_chart(
                    LineBasevalues, indicator, yaxis_title, color_palette=color_palette
                )
                fig = create_line_chart(
                    lineSecondaryvalues, indicator, yaxis_title, secondary=True, fig=fig
                )
            else:
                barvalues = indicator_df[indicator_df["xSecondary"] == "B"]
                linevalues = indicator_df[indicator_df["xSecondary"] == "L"]
                fig = create_bar_chart(
                    barvalues, indicator, yaxis_title, value_type, Stacked=False
                )
                fig = create_line_chart(
                    linevalues, indicator, yaxis_title, secondary=True, fig=fig
                )

        else:
            if chart_type == "Bar":
                fig = create_bar_chart(
                    indicator_df, indicator, yaxis_title, value_type, Stacked=False
                )
            elif chart_type == "StackedBar":  # Add support for Horizontal Bar chart
                fig = create_bar_chart(
                    indicator_df, indicator, yaxis_title, value_type, Stacked=True
                )
            elif chart_type == "HBar":  # Add support for Horizontal Bar chart
                fig = create_bar_chart(
                    indicator_df,
                    indicator,
                    yaxis_title,
                    value_type,
                    horizontal=True,
                    Stacked=False,
                )

            # Append the data table to the charts
            #   charts.append(html.Div([data_table]))
            elif chart_type == "Line":
                # fig = create_line_chart(indicator_df, indicator, yaxis_title)
                fig = create_line_chart(
                    indicator_df, indicator, yaxis_title, color_palette=color_palette
                )

            elif chart_type == "Table":
                isPivot = indicator_df["ISPivot"].iloc[0]

                Indicator = indicator_df["Indicator"].iloc[0]
                if isPivot == 1:
                    headers = create_dynamic_header(indicator_df)
                    pivot_df = indicator_df.pivot(
                        index="Xcolumns", columns="Colors", values="Values"
                    ).reset_index()
                    columns = [{"name": i, "id": i} for i in pivot_df.columns]
                    tables.append(
                        create_table_with_subheader(
                            indicator, headers, pivot_df.to_dict("records"), "table1"
                        )
                    )

                elif isPivot == 2:
                    FirstColumnTitle = indicator_df["FirstColumnHeader"].iloc[0]

                    multi_index = pd.MultiIndex.from_product(
                        [
                            indicator_df["Colors"].unique(),
                            indicator_df["SubHeader"].unique(),
                        ],
                        names=["Colors", "SubHeader"],
                    )
                    df2 = pd.DataFrame(
                        index=indicator_df["Xcolumns"].unique(), columns=multi_index
                    ).sort_index()

                    for row in indicator_df.itertuples():
                        df2.loc[row.Xcolumns, (row.Colors, row.SubHeader)] = row.Values

                    data_for_dash = convert_df_to_dict(df2)

                    columns = [
                        {
                            "name": "",
                            "id": "index",
                        }
                    ] + [
                        {"name": [x1, x2], "id": f"{x1}_{x2}"}
                        for x1, x2 in df2.columns
                        if x2
                    ]

                    dynamicTable = html.Div(
                        [
                            html.Label(
                                Indicator,
                                style={
                                    "textAlign": "center",
                                    "display": "block",
                                    "margin-bottom": "10px",
                                },
                            ),
                            DataTable(
                                id="table",
                                columns=columns,
                                data=data_for_dash,
                                merge_duplicate_headers=True,
                                style_header={"textAlign": "center"},
                                style_data={"textAlign": "center"},
                                style_cell_conditional=[
                                    {
                                        "if": {
                                            "column_id": "index"
                                        },  # Assuming 'index' is the ID for your first column
                                        "textAlign": "left",  # Align text to left for the first column
                                    }
                                ],
                            ),
                        ],
                        style={
                            "border": "1px solid silver",  # Adding a 1px solid border
                            "padding": "10px",
                            "margin-top": "10px",
                            "margin-bottom": "10px",  # Optional: Adds space between charts
                        },
                    )
                    tables.append(dynamicTable)
                else:
                    pivot_df = indicator_df.pivot(
                        index="Xcolumns", columns="Colors", values="Values"
                    ).reset_index()
                    pivot_df.rename(
                        columns={"Xcolumns": FirstColumnTitle}, inplace=True
                    )
                    columns = [{"name": col, "id": col} for col in pivot_df.columns]
                    tables.append(
                        create_table_with_subheader(
                            indicator,
                            columns,
                            pivot_df.to_dict("records"),
                            "table_default",
                        )
                    )

            elif chart_type == "Map":
                MapYear = indicator_df["Year"].iloc[0]

                fig = create_choropleth_map(indicator_df, geojson, color_map, MapYear)

            elif chart_type == "Cart":
                cards = [
                    create_indicator_card(row["Xcolumns"], row["Values"])
                    for _, row in indicator_df.iterrows()
                ]
                # Organize cards in a row

                cards_layout = html.Div(
                    [
                        html.Label(
                            indicator,
                            style={
                                "textAlign": "center",
                                "display": "block",
                                "margin-bottom": "10px",
                            },
                        ),
                        dbc.Row([dbc.Col(card) for card in cards], className="mb-4"),
                    ],
                    style={
                        "border": "1px solid silver",  # Adding a 1px solid border
                        "padding": "10px",
                        "margin-top": "10px",
                        "margin-bottom": "10px",  # Optional: Adds space between charts
                    },
                )
            elif chart_type == "MultiPieChart":
                years = indicator_df["Year"].unique()
                # Determine the layout for subplots
                rows = 1  # Adjust based on your preference
                cols = len(years)  # One column for each year

                # Create subplot figure
                fig = make_subplots(
                    rows=rows,
                    cols=cols,
                    specs=[[{"type": "pie"}] * cols],
                    subplot_titles=[str(int(year)) for year in years],
                    vertical_spacing=0.2,
                )

                for i, year in enumerate(years, start=1):
                    # Filter the DataFrame for the current year
                    df_filtered = indicator_df[indicator_df["Year"] == year]

                    # Create the pie chart for the current year
                    fig.add_trace(
                        go.Pie(
                            labels=df_filtered["Xcolumns"],
                            values=df_filtered["Values"],
                            name=str(year),
                        ),
                        row=1,
                        col=i,
                    )
                    fig.update_layout(
                        title_text=indicator,
                        title_x=0.5,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.5,
                            xanchor="center",
                            x=0.5,
                        ),
                    )

        if chart_type == "Table":
            charts.extend(tables)
        elif chart_type == "Cart":
            charts.append(cards_layout)

        else:
            # Append the figure wrapped in a dcc.Graph component to the list of charts
            graph_with_border = html.Div(
                dcc.Graph(figure=fig),
                style={
                    "border": "1px solid silver",  # Adding a 1px solid border
                    "padding": "10px",
                    "margin-top": "10px",
                    "margin-bottom": "10px",  # Optional: Adds space between charts
                },
            )
            charts.append(graph_with_border)  # Add charts to the charts list

    return charts


# New Code


def convert_df_to_dict(df):
    # Reset the index to include it as a regular column
    df_reset = df.reset_index()

    # Create a list of dictionaries from the DataFrame rows
    dict_list = df_reset.to_dict("records")

    # Modify the keys in each dictionary to match the DataTable format
    formatted_dict_list = []
    for record in dict_list:
        formatted_record = {}
        for key, value in record.items():
            if isinstance(key, tuple):
                # Convert tuple to a string ID that matches the DataTable format
                # Handle both single-level and MultiIndex columns
                new_key = "_".join(str(item) for item in key if item)
                formatted_record[new_key] = value
            else:
                # Handle regular columns
                formatted_record[key] = value
        formatted_dict_list.append(formatted_record)

    return formatted_dict_list

    single_array = []

    for _, row in df.iterrows():
        # First array with 'Xcolumns' and its value
        single_array.append(["Xcolumns", row["Xcolumns"]])

        # Second array with concatenated 'Indicator', 'Xcolumns', and 'Colors' values and the 'Values' data
        combined_string = f"{row['Xcolumns']}{row['SubHeader']}{row['Colors']}"
        single_array.append([combined_string, row["Values"]])

    return single_array


def create_dynamic_header(df):
    # Initialize an empty list for headers

    headers = []

    # Add 'Year' column as the first level header
    headers.append({"name": " ", "id": "Xcolumns"})

    # Iterate through unique 'Colors' values to create subheaders
    unique_colors = df["Colors"].unique()

    for color in unique_colors:
        # Check if there's a corresponding 'SubHeader' value for this color
        subheader = df[df["Colors"] == color]["SubHeader"].iloc[0]
        subheader_list = [str(color)]

        if subheader:
            subheader_list.append(subheader)
        headers.append({"name": subheader_list, "id": str(color)})

    return headers


def create_bar_chart(
    df, title, yaxis_title, value_type, horizontal=False, Stacked=False
):
    df["Xcolumns"] = df["Xcolumns"].astype(str)
    axis_labels = {
        "Xcolumns": yaxis_title if horizontal else "Category",
        "Values": "Value",
        "Colors": "Year",
    }

    orientation = "h" if horizontal else "v"
    barmode = "stack" if Stacked else "group"
    text = "%{text}%" if value_type == "P" else "%{text:.2f}"

    fig = px.bar(
        df,
        x="Values" if horizontal else "Xcolumns",
        y="Xcolumns" if horizontal else "Values",
        color="Colors",
        title=title,
        labels=axis_labels,
        orientation=orientation,
        color_discrete_sequence=color_palette,
        text="Values",
        barmode=barmode,
        hover_data={"YOYPercentageChange": ":.2f"},
    )

    fig.update_traces(texttemplate=text)

    yaxis_config = dict(
        visible=(
            False if df["ChartType"].iloc[0] == "StackedBar" else True
        ),  # Hide y-axis for StackedBar
        title="",
        type="category" if horizontal else "linear",
        autorange="reversed" if horizontal else True,
    )

    fig.update_layout(
        xaxis_title="",
        yaxis=yaxis_config,
        legend_title_text="",
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        title={
            "text": title,
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 14},
        },
        showlegend=bool(
            len(df["Colors"].unique()) > 1 or df["xSecondary"].notnull().any()
        ),
    )
    return fig


# Create LineChart


# Assuming 'df' is your DataFrame
df["HoverText"] = df.apply(
    lambda row: f"Year:{row['Year']},<br> QOM:{row['QOM']},Value: {row['Values']}<br>"
    f"{ 'MOM/QOQ' if row['ContainMonthlyPercentage'] == 1 else 'YOY' } "
    f"Percentage Change: {row['YOYPercentageChange']}%",
    axis=1,
)


def create_line_chart(
    df,
    title,
    yaxis_title,
    secondary=False,
    fig=None,
    color_palette=None,
):
    # Initialize figure for primary chart, use existing figure for secondary chart
    if not secondary or fig is None:
        fig = go.Figure()

    # Add a scatter plot trace for each 'Colors' group
    for color in df["Colors"].unique():
        df_by_color = df[df["Colors"] == color]

        trace_properties = dict(
            x=df_by_color["Xcolumns"].astype(str),
            y=df_by_color["Values"],
            mode="lines+markers",
            name=color,
            hovertemplate=df_by_color["HoverText"],
            line_shape="spline",
        )

        if secondary:
            trace_properties.update(yaxis="y2")

        fig.add_trace(go.Scatter(**trace_properties))

    # Buffer logic
    min_y = df["Values"].min()
    max_y = df["Values"].max()
    range_y = max_y - min_y
    buffer = 0.1 * range_y  # 10% buffer

    yaxis_range = [min_y - buffer, max_y + buffer]

    # Update layout
    if not secondary:
        fig.update_layout(
            title={
                "text": title,
                "y": 0.9,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
                "font": {"size": 14},
            },
            yaxis=dict(range=yaxis_range, tickformat=".2f"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.5,  # Adjust this value to move the legend up or down
                xanchor="center",
                x=0.5,
            ),
        )
    else:
        fig.update_layout(
            yaxis2=dict(
                title="",
                overlaying="y",
                side="right",
                anchor="x",
                range=yaxis_range,
                showgrid=False,
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.5,  # Adjust this value to move the legend up or down
                xanchor="center",
                x=0.5,
            ),
        )

    # Buffer logic and layout updates (as previously defined)

    return fig


# Creating Cards
def create_indicator_card(title, value):
    formatted_value = format_number_with_thousands_separator(value)
    card = dbc.Card(
        [
            dbc.CardHeader(title, className="text-center"),
            dbc.CardBody(
                [
                    html.Label(
                        formatted_value, className="card-title text-center d-block"
                    ),
                ]
            ),
        ],
        style={"width": "14rem", "margin": "10px"},  # Adjust styling as needed
    )
    return card


def format_number_with_thousands_separator(number):
    return "{:,}".format(number)


def create_table_with_subheader(indicator, headers, data, table_id):
    """
    Create a Dash HTML table component wrapped in a div with a label.

    Parameters:
    - indicator: The label text for the table.
    - columns: A list of dictionaries defining the table columns.
    - data: Data to display in the table, as a list of dictionaries.
    - table_id: The ID to assign to the DataTable component.

    Returns:
    - A Dash html.Div component containing the label and DataTable.
    """
    return html.Div(
        [
            html.Label(
                indicator,
                style={
                    "textAlign": "center",
                    "display": "block",
                    "margin-bottom": "10px",
                },
            ),
            DataTable(
                id=table_id,
                columns=headers,
                data=data,
                merge_duplicate_headers=True,
                style_header={"textAlign": "center"},
                style_data={"textAlign": "center"},
                style_cell_conditional=[
                    {
                        "if": {
                            "column_id": headers[0]["id"]
                        },  # Assuming the first column ID is accurate
                        "textAlign": "left",
                    }
                ],
            ),
        ],
        style={
            "border": "1px solid silver",
            "padding": "10px",
            "margin-top": "10px",
            "margin-bottom": "10px",
        },
    )



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
