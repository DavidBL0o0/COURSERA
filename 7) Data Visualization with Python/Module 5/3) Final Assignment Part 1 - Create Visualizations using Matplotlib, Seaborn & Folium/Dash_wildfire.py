import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update
import datetime as dt
import requests
import io

# Create app
app = dash.Dash(__name__)

# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Read the wildfire data into pandas dataframe
df = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/Historical_Wildfires.csv')

response = requests.get("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv")
response.raise_for_status()
csv_content = io.StringIO(response.text)
df_1 = pd.read_csv(csv_content)

# Extract year and month from the date column
df['Month'] = pd.to_datetime(df['Date']).dt.month_name()  # used for the names of the months
df['Year'] = pd.to_datetime(df['Date']).dt.year

# Layout Section of Dash
app.layout = html.Div(children=[
    html.H1('Australia Wildfire Dashboard 🧑‍🚒🚒🔥🔥🔥', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 26}),
    
    # Dropdown to select vehicle type
    html.Div([
        html.H2('Select Vehicle Type:', style={'margin-right': '2em'}),
        dcc.Dropdown(df_1['Vehicle_Type'].unique(), value='Supperminicar', id='vehicle-type')
    ]),
    
    # Graphs
    html.Div([
        dcc.Graph(id='pie-chart'),
        dcc.Graph(id='line-chart')
    ]),
    
    # TASK 2: Add the radio items and a dropdown right below the first inner division
    # outer division starts
    html.Div([
        # First inner divsion for adding dropdown helper text for Selected Drive wheels
        html.Div([
            html.H2('Select Region:', style={'margin-right': '2em'}),
            # Radio items to select the region
            dcc.RadioItems([
                {"label": "New South Wales", "value": "NSW"},
                {"label": "Northern Territory", "value": "NT"},
                {"label": "Queensland", "value": "QL"},
                {"label": "South Australia", "value": "SA"},
                {"label": "Tasmania", "value": "TA"},
                {"label": "Victoria", "value": "VI"},
                {"label": "Western Australia", "value": "WA"}
            ], "NSW", id='region', inline=True)
        ]),
        # Dropdown to select year
        html.Div([
            html.H2('🗓️ Select Year 🗓️:', style={'margin-right': '2em'}),
            dcc.Dropdown(df.Year.unique(), value=2005, id='year')
        ]),
        # TASK 3: Add two empty divisions for output inside the next inner division.
        # Second Inner division for adding 2 inner divisions for 2 output graphs
        html.Div([
            html.Div([], id='plot1'),
            html.Div([], id='plot2')
        ], style={'display': 'flex'}),
        # Add two empty divisions for output inside the next inner division for the two graphs of df_1
        html.Div([
            html.Div([], id='plot3'),
            html.Div([], id='plot4')
        ], style={'display': 'flex'}),
    ])
    # outer division ends
])

# layout ends

# TASK 4: Add the Output and input components inside the app.callback decorator.
# Place to add @app.callback Decorator
@app.callback(
    [Output('pie-chart', 'figure'),
     Output('line-chart', 'figure'),
     Output(component_id='plot1', component_property='children'),
     Output(component_id='plot2', component_property='children'),
     Output(component_id='plot3', component_property='children'),
     Output(component_id='plot4', component_property='children')],
    [Input('vehicle-type', 'value'),
     Input(component_id='region', component_property='value'),
     Input(component_id='year', component_property='value')]
)
# TASK 5: Add the callback function.
# Place to define the callback function.
def update_graphs(selected_vehicle_type, input_region, input_year):
    # Filter the data
    Rdata = df_1[df_1['Recession'] == 1]
    
    # Calculate the total advertising expenditure by vehicle type during recessions
    VTexpenditure = Rdata.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
    
    # Create pie chart
    pie_fig = px.pie(VTexpenditure, values='Advertising_Expenditure', names='Vehicle_Type', title='Share of Each Vehicle Type in Total Expenditure during Recessions')
    
    # Filter data for selected vehicle type
    vehicle_data = df_1[df_1['Vehicle_Type'] == selected_vehicle_type]
    
    # Create line chart
    line_fig = px.line(vehicle_data, x='Date', y='Automobile_Sales', title=f'Automobile Sales for {selected_vehicle_type}')
    
    # Data for wildfire plots
    region_data = df[df['Region'] == input_region]
    y_r_data = region_data[region_data['Year'] == input_year]
    
    # Plot one - Monthly Average Estimated Fire Area
    est_data = y_r_data.groupby('Month')['Estimated_fire_area'].mean().reset_index()
    fig1 = px.pie(est_data, values='Estimated_fire_area', names='Month', title="{} : Monthly Average Estimated Fire Area in year {}".format(input_region, input_year))
    
    # Plot two - Monthly Average Count of Pixels for Presumed Vegetation Fires
    veg_data = y_r_data.groupby('Month')['Count'].mean().reset_index()
    fig2 = px.bar(veg_data, x='Month', y='Count', title='{} : Average Count of Pixels for Presumed Vegetation Fires in year {}'.format(input_region, input_year))
    
    # Additional plots for df_1
    fig3 = px.histogram(vehicle_data, x='Date', y='Advertising_Expenditure', title=f'Advertising Expenditure for {selected_vehicle_type}')
    fig4 = px.scatter(vehicle_data, x='Date', y='Automobile_Sales', title=f'Automobile Sales Scatter for {selected_vehicle_type}')
    
    return pie_fig, line_fig, dcc.Graph(figure=fig1), dcc.Graph(figure=fig2), dcc.Graph(figure=fig3), dcc.Graph(figure=fig4)

if __name__ == '__main__':
    app.run_server()
