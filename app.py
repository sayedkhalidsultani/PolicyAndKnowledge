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

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
# Make sure to change this path when you upload it to github.
excel_file = 'Result.csv'
df = pd.read_csv(excel_file)
color_palette = ['#b2182b', '#ef8a62', '#fddbc7', '#d1e5f0', '#67a9cf', '#34495E']
app.layout = html.Div([
    dbc.Spinner(html.Div(id="loading-output"), spinner_style={"width": "3rem", "height": "3rem"}, color="primary", fullscreen=True),
    dbc.Container([
        dbc.Row(dbc.Col(html.H3("Policy And Knowledge Unit"), width=12), justify='center'),
        dbc.Row(
            dbc.Col(
                [
                    dcc.Dropdown(
                        id='category-dropdown',
                          options=[{'label': str(i) if i else 'Default', 'value': str(i) if i else 'Default'}
                             for i in df['Category'].dropna().unique()],
                            value=str(df['Category'].dropna().unique()[0]) 
                            ),
                    # This Div will contain the chart and summaries split into two columns
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(html.Div(id='charts-ouput'), width=12)
                                ]
                            )

                        ],
                        id='charts-container'
                    )
                ],
                width=12
            ),
            justify='center'
        ),
        dbc.Row(dbc.Col(html.H6(""), width=12), justify='right')
    ], style={'maxWidth': '1024px', 'margin': '10px auto', 'border': '1px solid silver', 'background': 'white','padding-bottom':'20px'}),
], style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'space-between', 'background': 'silver'})

# Addition of UniqueID



def dynamic_calculation(df):
    df_copy = df.copy()
    df_copy.sort_values(by='SortOrder', inplace=True)
    calculated_values = {}

    for index, row in df_copy.iterrows():
        calculation = row['Calculation']
        if pd.isna(calculation) or calculation.strip() == '':
            # If calculation is NaN or empty, use the existing Values
            calculated_values[row['UniqueID']] = row['Values']
            continue

        # Replace placeholders in the calculation string with actual values
        for placeholder in df_copy['UniqueID']:
            # Check if the placeholder is in the calculation string
            if placeholder in calculation:
                # Get the value for the placeholder
                value = df_copy.loc[df_copy['UniqueID'] == placeholder, 'Values'].iloc[0]
                # If the value is NaN, skip this placeholder
                if pd.isna(value):
                    print(f"Skipping placeholder {placeholder} because its value is NaN")
                    continue
                # Replace the placeholder with its value in the calculation string
                calculation = calculation.replace(placeholder, str(value))
        
        # Evaluate the calculation string
        try:
            calculated_values[row['UniqueID']] = eval(calculation)
        except Exception as e:
            print(f"Error evaluating calculation for {row['UniqueID']}: {e}")
            calculated_values[row['UniqueID']] = np.nan  # Use np.nan to represent a failed calculation

    # Update the original DataFrame with the calculated values
    for unique_id, value in calculated_values.items():
        df.loc[df['UniqueID'] == unique_id, 'Values'] = value



# Define the callback to update the bar charts
@app.callback(
    Output('charts-ouput', 'children'),
    [Input('category-dropdown', 'value')]
)
def update_bar_charts(selected_category):
    # Filter the DataFrame based on selected category
    filtered_df = df[df['Category'] == selected_category]


      # Ensure 'Colors' is treated as categorical data for grouping
    filtered_df['Colors'] = filtered_df['Colors'].astype(str)
    
    # Get a list of all indicators for the selected category
    df['Indicator'] = df['Indicator'].str.strip()

    indicators = filtered_df['Indicator'].unique()

   


  
    # Create a bar chart for each indicator
    charts = []
    tables=[]
    for indicator in indicators:
        indicator_df = filtered_df[filtered_df['Indicator'] == indicator]

        indicator_df['SortOrder'] = indicator_df['SortOrder'].fillna(0.0)

        indicator_df['SortOrder'] = pd.to_numeric(indicator_df['SortOrder'], errors='coerce')
        indicator_df.sort_values(by=['SortOrder','Indicator'], inplace=True)
      


        # if 'Calculation' in indicator_df.columns:
        #             indicator_df['Values'] = indicator_df.apply(lambda row: dynamic_calculation(row, indicator_df), axis=1)

        # Use the function to update the DataFrame before you start creating charts or tables
        

       

      

        chart_type = indicator_df['ChartType'].iloc[0]
      

        summary_df = indicator_df.groupby(['Indicator','Colors'])['Values'].describe(include='all')
        yaxis_title = indicator_df['YaxisTitle'].iloc[0]
        if pd.isna(yaxis_title):
            yaxis_title = ""
        # Get Percentage
        value_type = indicator_df['ValueType'].iloc[0]  # Extracting the ValueType  
    # Check for secondary chart requirement
        secondary_df = indicator_df[indicator_df['xSecondary'].notnull()]
        if not secondary_df.empty:
               barvalues=indicator_df[indicator_df['xSecondary']=='B']
               linevalues=indicator_df[indicator_df['xSecondary']=='L']
               
               fig = create_bar_chart(barvalues, indicator,yaxis_title,value_type)
               add_secondary_chart(fig,linevalues , 'Line')
 
        else:
           
            if chart_type == 'Bar':
                fig = create_bar_chart(indicator_df, indicator,yaxis_title,value_type)
            if chart_type == 'Table':
                table_header = html.Label(indicator, style={'textAlign': 'center', 'margin-top': '10px','font-size':'14px','display':'block'})
                dynamic_calculation(indicator_df)
               # Pivot the DataFrame to get "Year" columns as part of the data
             
                pivot_df = indicator_df.pivot_table(
                    values='Values',
                    index='Xcolumns',
                    columns='Year',
                    aggfunc='first'
                ).reset_index()
                # Filter out the row with 'Xcolumns' as its value

                # After Sorting Join it back to get correct sort order

                pivot_df = pivot_df.merge(
                    indicator_df[['Xcolumns', 'SortOrder']].drop_duplicates(),
                    on='Xcolumns',
                    how='left'
                ).drop_duplicates('Xcolumns').sort_values(by='SortOrder')

                # Now sort pivot_df by SortOrder
                pivot_df.sort_values(by='SortOrder', inplace=True)

                # Remove the SortOrder column if you don't want it in your final table
                pivot_df.drop(columns=['SortOrder'], inplace=True)



               
                # Create a list of columns for DataTable
              # Create a list of columns for DataTable
                columns = [{'name': 'Indicator', 'id': 'Xcolumns'}] + [
                {
                    'name': str(int(year)),  # Convert year to integer to remove decimals
                    'id': str(year),
                    'type': 'numeric',
                    'format': Format(precision=2, scheme=Scheme.fixed)  # Format for two decimal places
                }
                for year in pivot_df.columns if year != 'Xcolumns'
            ]

                # Create the data table component
        

                data_table = DataTable(
                    id=f'table-{indicator}',
                    columns=columns,
                    data=pivot_df.to_dict('records'),
                    column_selectable=False,
                    style_table={'overflow': 'auto','border':'1px solid silver'},
                    style_cell={'textAlign': 'left'},
                    # style_header={
                    #     'textAlign': 'center'
                    # },
                    # style_data_conditional=[
                    #     {
                    #         'if': {'column_id': str(year)},
                    #         'textAlign': 'center'  # Center-align the numerical columns
                    #     }
                    #     for year in pivot_df.columns if year != 'Xcolumns'
                    # ]
                )  

                # adding border to dynamic datatable
                data_table_with_border = html.Div(
                    [table_header, data_table],
                    style={
                        'border': '1px solid silver',  # Adding a 1px solid border
                        'padding': '10px',
                        'margin-top': '10px',
                        'margin-bottom': '10px'  # Adds space between tables
                    }
                )

           

            # Append the data table to the charts
             #   charts.append(html.Div([data_table]))
            if chart_type == 'Line':
                fig = create_line_chart(indicator_df, indicator,yaxis_title)
                      

       
         # Append the figure wrapped in a dcc.Graph component to the list of charts
        graph_with_border = html.Div(
                dcc.Graph(figure=fig),
                style={
                    'border': '1px solid silver',  # Adding a 1px solid border
                    'padding': '10px',
                    'margin-top':'10px',
                    'margin-bottom': '10px'  # Optional: Adds space between charts
                }
            )
        if chart_type == 'Table':
                # ... [code to create table]
                  tables.append(data_table_with_border)  # Add tables to the tables list
        else:
                # ... [code to create chart]
                charts.append(graph_with_border)  # Add charts to the charts list

    # Append tables at the end of the charts
        charts.extend(tables)
        

               
        #charts.append(graph_with_border)
        
        # Adding Summary

        # Add Summary for percentage Functions
         # Create a custom aggregation function
        def custom_agg(group):
            # To Exclude sum for rows containing Avg
            if 'Avg' in group['Xcolumns'].iloc[0]:
                return ""  # Return a blank string for rows with 'Avg'
            if group['ValueType'].iloc[0] == 'P':  # Check if the group is for percentages
                # Sum the values after converting to float, divide by 100, and then multiply by 100
                total_sum = indicator_df['Values'].sum()
                percentage = (group['Values'].astype(float).sum() / total_sum) * 100
                return round(percentage, 2)  # Round the
            else:
                 sum_value = group['Values'].sum()
                 return round(sum_value, 2)
     
        #indicator_df = filtered_df[filtered_df['Indicator'] == indicator]
            # Check if 'xSecondary' column has any non-null values
        secondary_df = indicator_df[indicator_df['xSecondary'].notnull()]
        if not secondary_df.empty:
            indicator_df = indicator_df[indicator_df['xSecondary'].str.contains('B')]
            summary_df = indicator_df.groupby('Year').apply(custom_agg).reset_index()
            summary_df.columns = ['Year', 'Sum']
        else:
            summary_df = indicator_df.groupby('Xcolumns', sort=False).apply(custom_agg).reset_index()
            summary_df.columns = ['Xcolumns', 'Sum' if indicator_df['ValueType'].iloc[0] != 'P' else 'Percentage']

        # Add mean, min, max calculations to summary_df
        additional_stats = indicator_df.groupby('Xcolumns',sort=False)['Values'].agg(['mean', 'min', 'max']).reset_index(drop=True)
        summary_df = pd.concat([summary_df, additional_stats], axis=1)
  
        # Round the numerical values to two decimal places
        summary_df = summary_df.round(2)
     
        #summary_df.sort_values(by='Xcolumns', inplace=True)
   
        # Rename the first column
        columns = [{"name": "Indicators" if i == "Xcolumns" else i, "id": i} for i in summary_df.columns]
        # Add title for each Summary
        summary_title = html.Label(f"Summary", style={'textAlign': 'center', 'color': '#yourColorCode','display':'block','margin-bottom':'10px'})
              
        table = DataTable(
                id=f'table-{indicator}',
                columns=columns,
                data=summary_df.to_dict('records'),
                style_table={'overflow': 'auto','border':'1px solid silver'},
                style_cell={'textAlign': 'left'},
                export_format="csv",  # Enable export to CSV
                export_headers="display",
            
            )
        charts.append(html.Div([summary_title, table]))
   
    return charts

# New Code

def create_bar_chart(df, title,yaxis_title,value_type):
    df['Xcolumns'] = df['Xcolumns'].astype(str)
    fig = px.bar(
        df,
        x='Xcolumns',
        y='Values',
        color='Colors',
        title=title,
        labels={'Xcolumns': 'Category', 'Values': 'Value', 'Colors': 'Year'},
        barmode='group',
        color_discrete_sequence=color_palette,
        text='Values'
    )
    fig.update_layout(
        title={
            'text': title,
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 14}
        },
        showlegend=True,
        legend_title_text='',
        legend=dict(
            orientation='h',
            yanchor="bottom",
            y=-0.3,  # Adjust if necessary
            xanchor="center",
            x=0.5
        ),
        xaxis_title="",  # Hide the x-axis title
        yaxis_title=yaxis_title
    )

    # Display negative values also in chart
    
     # Ensure the Y-axis range includes both the minimum and maximum values from 'Values'
    # min_value = df['Values'].min()
    # max_value = df['Values'].max()

    # buffer = abs(min_value * 0.1) if min_value < 0 else 0

    # fig.update_yaxes(range=[min_value - buffer, max_value])

     # Format Y-axis ticks and data labels as percentages if value_type is 'P'
    if value_type == 'P':
        max_value = df['Values'].max()  # Assuming 'Values' holds the data you're plotting
        # Before creating the range for tick values, check if max_value is NaN
        if pd.isna(max_value):
            max_value = 0  # or some other default value that makes sense for your context
        else:
            max_value = int(max_value)

        tick_values = list(range(0, int(max_value) + 1, 10))  # Change step as needed
        tick_labels = [f'{x}%' for x in tick_values]
    
        fig.update_layout(
           yaxis=dict(
                tickmode='array',
                tickvals=tick_values,
                ticktext=tick_labels
            )
        )
        fig.update_traces(
            texttemplate='%{text}%',  # Add '%' to the bar labels
        )
    else:  # Handling for numerical values (value_type='N')
    # Format Y-axis and bar labels as numbers with a thousand separator
        fig.update_traces(
            texttemplate='%{y:,.0f}'  # Add thousand separator to bar labels
        )
        fig.update_layout(
            yaxis_tickformat=',',  # Add thousand separator to Y-axis ticks
        )


    return fig

def create_line_chart(df, title,yaxis_title):
    fig = go.Figure()
 # Add a scatter plot trace for each 'Colors' group
    for color in df['Colors'].unique():
        df_by_color = df[df['Colors'] == color]
        fig.add_trace(go.Scatter(
            x=df_by_color['Xcolumns'],
            y=df_by_color['Values'],
            mode='lines+markers',  # Combine lines, markers, and text
            name=color,  # Use color for the legend name
            # text=df_by_color['Values'],  # Display values as text
            # textposition='bottom center',  # Position the text above markers
        ))

    # Update the layout of the figureclear
    fig.update_layout(
        title={
            'text': title,
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 14}
        },
        showlegend=True,
        legend_title_text='',
        legend=dict(
            orientation='h',
            yanchor="bottom",
            y=-0.3,  # Adjust if necessary
            xanchor="center",
            x=0.5
        ),
        xaxis_title="",  # Optionally hide the x-axis title
        yaxis_title=yaxis_title  # Optionally hide the y-axis title

    )


    return fig

def add_secondary_chart(fig, df, secondary_chart_type):
     if secondary_chart_type == 'Line':
        for color in df['Colors'].unique():
            secondary_color_df = df[df['Colors'] == color]
            fig.add_trace(
                go.Scatter(
                    x=secondary_color_df['Xcolumns'],
                    y=secondary_color_df['Values'],
                    mode='lines+markers+text',
                    line=dict(dash='dash'),
                    name='Total',
                    text=secondary_color_df['Values'],
                    textposition='top center'
                )
            )
     elif secondary_chart_type == 'Bar':
        df['Colors'] = df['Colors'].astype(str)
        color_mapping = {color: palette for color, palette in zip(df['Colors'].unique(), color_palette)}
        for color in df['Colors'].unique():
            secondary_color_df = df[df['Colors'] == color]
            fig.add_trace(
                go.Bar(
                    x=secondary_color_df['Xcolumns'],
                    y=secondary_color_df['Values'],
                    name=f'Secondary - {color}',
                    marker=dict(color=color_mapping[color]),  # Use color mapping,
                    text=secondary_color_df['Values'],
                    textposition='outside'
                )
            )
        fig.update_layout(barmode='group')



if __name__ == '__main__':
    app.run_server(debug=True)