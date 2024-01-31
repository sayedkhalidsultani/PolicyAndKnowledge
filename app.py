import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash.dash_table import DataTable
import numpy as np
from dash.dash_table.Format import Format, Scheme
from dash.dash_table import DataTable, FormatTemplate

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

app.layout = html.Div(
    [
        dbc.Spinner(
            html.Div(id="loading-output"),
            spinner_style={"width": "3rem", "height": "3rem"},
            color="primary",
            fullscreen=True,
        ),
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
                                        [dbc.Col(html.Div(id="charts-ouput"), width=12)]
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
    filtered_df.sort_values(by=["SortOrder", "Indicator"], inplace=True)

    # Ensure 'Colors' is treated as categorical data for grouping
    filtered_df["Colors"] = filtered_df["Colors"].astype(str)

    # Get a list of all indicators for the selected category
    df["Indicator"] = df["Indicator"].str.strip()

    indicators = filtered_df["Indicator"].unique()

    # Create a bar chart for each indicator
    charts = []
    tables = []

    def truncate_to_two_decimals(x):
        if isinstance(x, float):
            # Convert to string and split at the decimal point
            integer_part, decimal_part = str(x).split(".")
            # Truncate the decimal part and reform the number
            truncated = f"{integer_part}.{decimal_part[:2]}"
            return float(truncated)
        else:
            # Return the original value if it's not a float
            return x

    df["Values"] = df["Values"].apply(truncate_to_two_decimals)

    # Check for secondary

    for indicator in indicators:
        indicator_df = filtered_df[filtered_df["Indicator"] == indicator]

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
                indicator_value = indicator_df["Indicator"].iloc[0]
                table_title = html.Label(
                    f"{indicator}",
                    style={
                        "textAlign": "center",
                        "fontSize": "14px",
                        "display": "block",
                        "margin-top": "10px",
                        "margin-bottom": "10px",
                    },  # Add styling here
                )  #

                # Create a dynamic header based on the DataFrame
                header = create_dynamic_header(indicator_df)

                pivot_df = indicator_df.pivot(
                    index="Xcolumns", columns="Year", values="Values"
                )
                pivot_df.reset_index(inplace=True)
                dynamicTable = html.Div(
                    [
                        table_title,
                        DataTable(
                            id="table-multicolumn",
                            columns=header,
                            data=pivot_df.to_dict("records"),
                            merge_duplicate_headers=True,  # Merge headers visually
                            # Additional settings
                            style_cell={"textAlign": "center"},
                            style_header={
                                "backgroundColor": "rgb(230, 230, 230)",
                                "font-size": "14px",
                            },
                            style_data={
                                "whiteSpace": "normal",
                                "height": "auto",
                                "font-size": "14px",
                            },
                        ),
                    ],
                    style={
                        "border": "1px solid silver",  # Adding a 1px solid border
                        "padding": "10px",
                        "margin-top": "10px",
                        "margin-bottom": "10px",  # Optional: Adds space between charts
                    },
                )

        if chart_type == "Table":
            charts.append(dynamicTable)
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
        visible=False
        if df["ChartType"].iloc[0] == "StackedBar"
        else True,  # Hide y-axis for StackedBar
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
