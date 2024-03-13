import dash
from dash import html, dcc, callback, Input, Output,State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash.dash_table import DataTable
import requests
from plotly.subplots import make_subplots
import math
from db_utils import execute_query
from datetime import datetime
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML

dash.register_page(__name__,path='/pandk/indicators')

color_palette = [
        "#00A08B",
        "#fc8d59",
            "#41ab5d",
        "#d1e5f0",
       "#67a9cf",
    "#9ecae1",
     "#778AAE",
    "#565656",

    "#edf8b1",
    "#ef8a62",
    "#7fcdbb",

 
    "#34495E",

    "#A777F1",
   
    "#ec7014",
    "#c6dbef",
     "#08306b",
]

rangeslider_marks = {2015:'2015',2016:'2016',2017:'2017',2018:'2018',
    
    2019:'2019', 2020:'2020', 2021:'2021', 2022:'2022', 2023:'2023',
                     2024:'2024', 2025:'2025'}

layout = html.Div(
    [
        # dcc.Store(id='store-data'),
        # dcc.Download(id="download-csv"),
        # html.Button("Download csv", id="btn-download-csv"),

                dbc.Container(
                    [
                        dbc.Row(
                            dbc.Col(
                                [
                                    dcc.Dropdown(
                                        id="category-dropdown",
                                        placeholder="Select a Category",
                                        style={'marginBottom': '10px' }),
                                    dcc.Dropdown(
                                        id="SubCategory-dropdown",
                                        placeholder="Select a SubCategory",
                                        style={'marginBottom': '10px'}),
                                    dcc.RangeSlider(min=2015,
                                               max=2025,
                                               value=[2015,2025],
                                        step=1,
                                        updatemode='mouseup',
                                        persistence=True,
                                        marks=rangeslider_marks,
                                        persistence_type='session', # 'memory' or 'local'
                                        id="Year-Slider"
                                ),
                                    
                                    html.Div(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        dbc.Row([
                                                            dbc.Col(
                                                                html.Div(
                                                                    [
                                                                html.Button('Export Data', id='btn-export',style={'display': 'none'}, n_clicks=0),
                                                                html.Button('Information', id='btn-popup',style={'display': 'none'}, n_clicks=0),
                                                                html.Div(id="charts-ouput")],style={'border':'1px solid silver','padding-left':'5px'}),width=12
                                                                ),
                                                            dcc.Store(id='store-data'),
                                                            dcc.Download(id="download-csv"),
                                                            dcc.Store(id='store-info'),
                                                            dbc.Modal(
                                                                    [
                                                                        dbc.ModalHeader(dbc.ModalTitle("Indicator Detail")),
                                                                        dbc.ModalBody("", id='modal-body'),
                                                                        dbc.ModalFooter(
                                                                            dbc.Button("Close", id='close-modal', className="ms-auto", n_clicks=0)
                                                                        ),
                                                                    ],
                                                                    id='info-modal',
                                                                    is_open=False,
                                                                ),
        
                                                        ])
                                                        
                                                        
                                                     
                                                    )
                                                ],
                                            ),
                                         
                                        ],
                                        id="charts-container",
                                    ),
                                ],
                                width=12,
                            ),
                            justify="center",
                            style={'marginTop':'10px'}
                        ),
                    ],style={'padding':'10px'}
                   
                ),
    ],
)


# Define the callback to update the bar charts
@callback(
            [Output("charts-ouput", "children"),Output('btn-export', 'style'),Output('store-data', 'data'),Output('store-info', 'data'),Output('btn-popup', 'style')],
             #Output('store-data', 'data')
            [Input("SubCategory-dropdown", "value"),Input("Year-Slider", "value")])
def update_bar_charts(selected_category,year_slider):

    SQL_QUERY = "SELECT Indicator, Xcolumns, FirstColumnHeader, SubHeader, Colors, Year, [Values], ChartType, Source, xSecondary, r.SortOrder, ISPivot, Lat, Lon, ValueType, YaxisTitle,c.SubCategory,PopupContent FROM Results R INNER JOIN dbo.Categories c ON c.ID=r.SubCategoryID where c.SubCategory= %s and r.year between %s  and %s"
    df = execute_query(SQL_QUERY, (selected_category,year_slider[0],year_slider[1]))
    
    # Filter the DataFrame based on selected category
    filtered_df = df #df[df["SubCategory"] == selected_category].copy()

    fig = {}


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

    # Show or hide buttons
        # Popup Info
    PopupText=None
    ShowInfoButton=None
    
    HideButton = {'display': 'none'}
    ShowButton = {'display': 'inline-block'}
    
    if selected_category is not None:
         ShowExportButtons=ShowButton
         ShowInfoButton=ShowButton
    else:
        ShowExportButtons=HideButton
        ShowInfoButton=HideButton
    

    if not df.empty:
        PopuInfo=df['PopupContent'].iloc[0]
        if pd.notnull(PopuInfo) and bool(PopuInfo):
           PopupText=PopuInfo
           ShowInfoButton=ShowButton
        else:
            ShowInfoButton=HideButton
            PopupText="No Information is available for given indicator"
    
    
    
    # Check for secondary
    for indicator in indicators:
        tables = []
       
        indicator_df = filtered_df[filtered_df["Indicator"] == indicator]
        Source = 'Source:'+indicator_df["Source"].iloc[0]


        yaxis_title = indicator_df["YaxisTitle"].iloc[0] if not pd.isna(indicator_df["YaxisTitle"].iloc[0]) else ""
        # Maps

        max_value = indicator_df["Values"].max()
        step = (max_value // 3) + 1
        color_map = {
            "0-{}".format(step): "#9ecae1",
            "{}-{}".format(step, 2 * step): "#41ab5d",
            "{}-{}".format(2 * step, 3 * step): "#edf8b1",
            ">{}".format(3 * step): "#ef8a62",
        }

        indicator_df["MapCategory"] = indicator_df["Values"].apply(categorize_value)

        indicator_df["SortOrder"] = indicator_df["SortOrder"].fillna(0.0)

        indicator_df["SortOrder"] = pd.to_numeric(
            indicator_df["SortOrder"], errors="coerce"
        )
        indicator_df.sort_values(by=["SortOrder", "Indicator"], inplace=True)

        chart_type = indicator_df["ChartType"].iloc[0]

        

       
   

        #yaxis_title = indicator_df["YaxisTitle"].iloc[0]
        if pd.isna(yaxis_title):
            yaxis_title = ""
        # Get Percentage
        value_type = indicator_df["ValueType"].iloc[0]  # Extracting the ValueType
        # Check for secondary chart requirement
        secondary_df = indicator_df["ValueType"].iloc[0]
        xsecondary = indicator_df["xSecondary"].iloc[0]
        isPivot = indicator_df["ISPivot"].iloc[0]

        if pd.notnull(indicator_df["xSecondary"].iloc[0]):
            xsecondary = indicator_df["xSecondary"].iloc[0]
        # Proceed with your condition
        else:
        # Handle the case where the value is null
            xsecondary = None

        if xsecondary=='B' or xsecondary=='L':
            ShowExportButtons=ShowButton
            if chart_type == "Line":
                LineBasevalues = indicator_df[indicator_df["xSecondary"] == "B"]
                lineSecondaryvalues = indicator_df[indicator_df["xSecondary"] == "L"]
                fig = create_line_chart(
                    LineBasevalues, indicator+'<br>('+Source+')', yaxis_title, color_palette=color_palette,color_index=0
                )
                fig = create_line_chart(
                    lineSecondaryvalues, indicator+'<br>('+Source+')', yaxis_title, secondary=True, fig=fig,color_palette=color_palette,color_index=1
                )
            else:
                barvalues = indicator_df[indicator_df["xSecondary"] == "B"]
                linevalues = indicator_df[indicator_df["xSecondary"] == "L"]
                fig = create_bar_chart(
                    barvalues, indicator+'<br>('+Source+')', yaxis_title, value_type, Stacked=False
                )
                fig = create_line_chart(
                    linevalues, indicator+'<br>'+'('+Source+')', yaxis_title, secondary=True, fig=fig,color_palette=color_palette
                )

        else:
            if chart_type == "Bar":
                ShowExportButtons=ShowButton
                fig = create_bar_chart(
                    indicator_df, indicator+'<br>'+'('+Source+')', yaxis_title, value_type, Stacked=False
                )
            elif chart_type == "StackedBar":  # Add support for Horizontal Bar chart
                ShowExportButtons=ShowButton
                fig = create_bar_chart(
                    indicator_df, indicator+'<br>'+'('+Source+')', yaxis_title, value_type, Stacked=True
                )
            elif chart_type == "HBar":  # Add support for Horizontal Bar chart
                ShowExportButtons=ShowButton
                fig = create_bar_chart(
                    indicator_df,
                    indicator+'<br>'+'('+Source+')',
                    yaxis_title,
                    value_type,
                    horizontal=True,
                    Stacked=False,
                )

            # Append the data table to the charts
            #   charts.append(html.Div([data_table]))
            elif chart_type == "Line" and (xsecondary!='B' or xsecondary!='L'):
                ShowExportButtons=ShowButton
                # fig = create_line_chart(indicator_df, indicator, yaxis_title)
                fig = create_line_chart(
                    indicator_df, indicator+'<br>'+'('+Source+')', yaxis_title, color_palette=color_palette
                )

            elif chart_type == "Table":
                unique_chart_types_per_subcategory = df.groupby('SubCategory')['ChartType'].nunique()

                # Check if any SubCategory has more than 1 unique ChartType
                if (unique_chart_types_per_subcategory > 1).any():
                    ShowExportButtons=ShowButton
                else:
                    ShowExportButtons=HideButton
        
          
                indicator_df['ISPivot'] = pd.to_numeric(indicator_df['ISPivot'], downcast='integer', errors='coerce')
                indicator_df['Year'] = pd.to_numeric(indicator_df['Year'], errors='coerce')


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
                            indicator, headers, pivot_df.to_dict("records"), "table1",Source
                        )
                    )

                elif isPivot == 2:
                    #BackGroundColor = indicator_df["BackgroundColor"].iloc[0]
                                                    
                   
                    FirstColumnTitle = indicator_df["FirstColumnHeader"].iloc[0]

                    indicator_df.sort_values(by='SortOrder', inplace=True)

                    xColumns=indicator_df["Xcolumns"].unique()

                    multi_index = pd.MultiIndex.from_product(
                        [
                            indicator_df["Colors"].unique(),
                            indicator_df["SubHeader"].unique(),
                        ],
                        names=["Colors", "SubHeader"],
                    )
                    df2 = pd.DataFrame(
                        index=xColumns, columns=multi_index
                    )

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
                    
                    quantiles = indicator_df['Values'].quantile([0.33, 0.66]).to_dict()

                    # low_threshold = quantiles[0.33]
                    # medium_threshold = quantiles[0.66]

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
                            html.Label(
                                '('+Source+')',
                                style={
                                    "textAlign": "center",
                                    "display": "block",
                                },
                            ),

                            DataTable(
                                id="table",
                                columns=columns,
                                export_format="csv",
                                data=data_for_dash,
                                fixed_columns={'headers': True, 'data': 1},
                                merge_duplicate_headers=True,
                                style_header={"textAlign": "center"},
                                style_data={"textAlign": "center"},
                                # style_data_conditional=[
                                #     # Conditional formatting for cells with zero
                                #     {
                                #         'if': {'column_id': col_id, 'filter_query': f'{{{col_id}}} = 0'},
                                #         'backgroundColor': 'black',
                                #         'color': 'white'
                                #     }
                                #     for col_id in [col['id'] for col in columns if col['id'] != 'index']  # Exclude the index column from formatting
                                # ] + [
                                #     # Conditional formatting for cells with values less than zero
                                #     {
                                #         'if': {'column_id': col_id, 'filter_query': f'{{{col_id}}} < 0'},
                                #         'backgroundColor': 'red',
                                #         'color': 'white'
                                #     }
                                #     for col_id in [col['id'] for col in columns if col['id'] != 'index']  # Exclude the index column from formatting
                                # ],
              
                                # style_cell_conditional=[
                                #     {
                                #         "if": {
                                #             "column_id": "index"
                                #         },  # Assuming 'index' is the ID for your first column
                                #         "textAlign": "left",  # Align text to left for the first column
                                #     }
                                # ],
                                style_table={
                                    'maxHeight': '600px',  # Adjust based on your needs
                                    'overflowY': 'auto',
                                    'overflowX': 'auto',
                                    'width': '100%',
                                    'minWidth': '100%',
                                },       
                            ),
                        ],
                        style={
                            "border": "0px solid silver",  # Adding a 1px solid border
                # Optional: Adds space between charts
                        },
                    )
                    tables.append(dynamicTable)
                else:
                    FirstColumnTitle = indicator_df["FirstColumnHeader"].iloc[0]
                    
                    

                    # Extract the sorted unique values from Xcolumns for desired_order
                    desired_order = indicator_df['Xcolumns'].unique()
                                
                    
                    pivot_df = indicator_df.pivot(
                        index="Xcolumns", columns="Colors", values="Values"
                    ).reset_index()

                    pivot_df.rename(
                        columns={"Xcolumns": FirstColumnTitle}, inplace=True
                    )

                    FirstColumnTitle = indicator_df["FirstColumnHeader"].iloc[0]
                    pivot_df.rename(columns={"Xcolumns": FirstColumnTitle}, inplace=True)

                    pivot_df[FirstColumnTitle] = pd.Categorical(pivot_df[FirstColumnTitle], categories=desired_order, ordered=True)
                    pivot_df.sort_values(by=FirstColumnTitle, inplace=True)

                    columns = [{"name": col, "id": col} for col in pivot_df.columns]
                    tables.append(
                        create_table_with_subheader(
                            Indicator,
                            columns,
                            pivot_df.to_dict("records"),
                            "table_default",Source
                        )
                    )
                    
            elif chart_type=='TreeMap':
                  ShowExportButtons=ShowButton
                  fig = go.Figure(go.Treemap(
                    labels=indicator_df["Xcolumns"],
                    values=indicator_df["Values"],
                    parents = [""] * len(indicator_df),
                    texttemplate="<b>%{label}</b><br>%{percentRoot:.2%}",
                    #texttemplate="<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percentRoot:.2%}",
                    marker=dict(colors=color_palette),
                    hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percentParent:.2%}<extra></extra>',  # Custom hover text
                ))
                  fig.update_layout(
                    title={
                        'text': Indicator+'-('+Source+')',
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        "font": {"size": 14},
                    }
                )

            elif chart_type == "Cart":
                ShowExportButtons=ShowButton
            
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
                         html.Label(
                            '('+Source+')',
                            style={
                                "textAlign": "center",
                                "display": "block"
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
                ShowExportButtons=ShowButton
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
                            marker=dict(colors=color_palette),
                        ),
                        row=1,
                        col=i,
                    )
                    fig.update_layout(
                        title_text=indicator+'-('+Source+')',
                        title_x=0.5,
                        title_font=dict(size=12),
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
                 # Adding a 1px solid border
                    "padding": "10px",
                    "margin-top": "10px",
                    "margin-bottom": "10px",  # Optional: Adds space between charts
                },
            )
            charts.append(graph_with_border)  # Add charts to the charts list

    # # giving UniqueID to each div
    # for index, indicator in enumerate(indicators):
    # # Your existing code to prepare the chart, e.g., fig = create_bar_chart(...)
    # # Assuming 'fig' is your Plotly figure object for the current 'indicator'
    
    # # Generate a unique ID for the div that will contain the dcc.Graph
    #     unique_div_id = f"chart-container-{indicator.replace(' ', '-').lower()}-{index}"
    #     graph_id = f"graph-{indicator.replace(' ', '-').lower()}-{index}"

    #     # Append the figure wrapped in a dcc.Graph component within a div to the list of charts
    #     graph_with_border_and_unique_id = html.Div(
    #         dcc.Graph(id=graph_id, figure=fig),
    #         id=unique_div_id,
    #         style={
    #             "border": "1px solid silver",  # Optional: Adding a border for visualization
    #             "padding": "10px",
    #             "margin-top": "10px",
    #             "margin-bottom": "10px",
    #         },
    #     )
    


    return charts,ShowExportButtons,filtered_df.to_dict('records'),PopupText,ShowInfoButton #,filtered_df.to_dict('records')


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
        #hover_data={"YOYPercentageChange": ":.2f"},
    )

    fig.update_traces(texttemplate=text)

    # if not df.empty and "ChartType" in df.columns:
    #         chart_type = df["ChartType"].iloc[0]
    #         y_axis_visibility = False if chart_type == "StackedBar" else True
    # else:
    #         # Handle the case where df is empty or doesn't contain "ChartType"
    #         # This might involve setting default values or skipping certain operations
    #        # chart_type = "DefaultType"  # Example default value or handle as appropriate
    #         y_axis_visibility = True  #


    yaxis_config = dict(
        visible=(
           True
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
            len(df["Colors"].unique()) > 1 or df['xSecondary'].isin(['B', 'L']).any()
        ),
    )
    return fig


# Create LineChart


# Assuming 'df' is your DataFrame
# df["HoverText"] = df.apply(
#     lambda row: f"Year:{row['Year']},<br> QOM:{row['QOM']},Value: {row['Values']}<br>"
#     f"{ 'MOM/QOQ' if row['ContainMonthlyPercentage'] == 1 else 'YOY' } "
#     f"Percentage Change: {row['YOYPercentageChange']}%",
#     axis=1,
# )


def create_line_chart(
    df,
    title,
    yaxis_title,
    secondary=False,
    fig=None,
    color_palette=None,
    color_index=7
):
    # Initialize figure for primary chart, use existing figure for secondary chart
    if not secondary or fig is None:
        fig = go.Figure()
    
    if color_palette is None or not color_palette:
        raise ValueError("color_palette must be provided and contain at least one color")

    # Add a scatter plot trace for each 'Colors' group
    unique_colors = df["Colors"].unique()
    #color_map = {color: palette_color for color, palette_color in zip(unique_colors, color_palette)}
    color_map = {color: color_palette[i % len(color_palette)] for i, color in enumerate(unique_colors)}

    for color in unique_colors:
        df_by_color = df[df["Colors"] == color]

        trace_properties = dict(
            x=df_by_color["Xcolumns"].astype(str),
            y=df_by_color["Values"],
            mode="lines+markers",
            name=color,
            #hovertemplate=df_by_color["HoverText"],
            line_shape="spline",
            line=dict(color=color_palette[color_index]),
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


def create_table_with_subheader(indicator, headers, data, table_id,Source):

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
            html.Label(
                '('+Source+')',
                style={
                    "textAlign": "center",
                    "display": "block"
                },
            ),
            DataTable(
                id=table_id,
                columns=headers,
                data=data,
                export_format="csv",
                merge_duplicate_headers=True,
                style_header={"textAlign": "center"},
                style_data={"textAlign": "center"},
                style_data_conditional=[
                    {
                        "if": {
                            "column_id": headers[0]["id"]
                        },  # Assuming the first column ID is accurate
                        "textAlign": "left",
                    }
                ],
                style_table={
                                    'maxHeight': '600px',  # Adjust based on your needs
                                    'overflowY': 'auto',
                                    'overflowX': 'auto',
                                    'width': '100%',
                                    'minWidth': '100%',
                                },
            ),
        ],
        style={
            "border": "1px solid silver",
            "padding": "10px",
            "margin-top": "10px",
            "margin-bottom": "10px",
        },
    )

# def highlight_max_row(df):
    df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
    return [
        {
            'if': {
                'filter_query': '{{id}} = {}'.format(i),
                'column_id': col
            },
            'backgroundColor': '#3D9970',
            'color': 'white'
        }
        # idxmax(axis=1) finds the max indices of each row
        for (i, col) in enumerate(
            df_numeric_columns.idxmax(axis=1)
        )
    ]


# Cascading Dropdownlist 

@callback(
    Output('category-dropdown', 'options'),
    [Input('loading-map', 'children')]  # Assuming 'page-content' is the ID of a Div in your layout that loads the entire page content
)
def populate_category_dropdown(_):
    df = execute_query("SELECT DISTINCT Category FROM dbo.Categories ORDER BY Category")  # Adjust query as needed
    options = [{'label': category, 'value': category} for category in df['Category'].dropna().unique()]
    return options

# Callback to update 'SubCategory-dropdown' based on selected category
@callback(
    Output('SubCategory-dropdown', 'options'),
    [Input('category-dropdown', 'value')]
)
def update_subcategory_dropdown(selected_category):
    if selected_category is not None:
        query = "SELECT SubCategory FROM dbo.Categories WHERE Category = %s"  # Use parameterized queries to prevent SQL injection
        df = execute_query(query, (selected_category,))
        options = [{'label': subcategory, 'value': subcategory} for subcategory in df['SubCategory'].dropna().unique()]
    else:
        options = []
    return options

@callback(
    Output("download-csv", "data"),
    Input("btn-export", "n_clicks"),
    [State('store-data', 'data')],
    prevent_initial_call=True,
)
def func(n_clicks,stored_data):
    if n_clicks is None or stored_data is None:
        raise PreventUpdate
    df = pd.DataFrame(stored_data)
    df = df.query("ChartType != 'Table'")
    columns_to_exclude = ['FirstColumnHeader', 'SubHeader','Year','ChartType','Source','xSecondary','SortOrder','ISPivot','Lat','Lon','ValueType','YaxisTitle','SubCategory','PopupContent']
    df = df.drop(columns=columns_to_exclude)
    df = df.rename(columns={
    'Xcolumns': 'XSeries',
    'Colors': 'Categories',
    })
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filenameprefix=df.iloc[0]['Indicator']
    filename = f"{filenameprefix}_{timestamp}.xlsx"  

    
    return dcc.send_data_frame(df.to_excel, filename, engine="xlsxwriter",index=False)

#Popup Content 
@callback(
    [Output('info-modal', 'is_open'), Output('modal-body', 'children')],
    [Input('btn-popup', 'n_clicks'), Input('close-modal', 'n_clicks')],
    [State('info-modal', 'is_open'), State('store-info', 'data')],
    prevent_initial_call=True,
)
def toggle_modal(btn_popup_clicks, close_modal_clicks, is_open, store_data):
    ctx = dash.callback_context

    # Determine which input triggered the callback
    if not ctx.triggered or ctx.triggered[0]['value'] == 0:
        return is_open, ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'btn-popup':
        # When the 'Information' button is clicked, open the modal and display data from dcc.Store
        return True, DangerouslySetInnerHTML(store_data)
    elif button_id == 'close-modal':
        # When the 'Close' button in the modal is clicked, close the modal
        return False, ""
    else:
        return is_open, ""  # Return the current state if neither button was clicked
