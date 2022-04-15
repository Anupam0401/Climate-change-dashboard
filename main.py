# import the required libraries
from logging import logThreads
import dash
import numpy as np
import pandas as pd
import plotly as py
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc, html

df = pd.read_csv("TemperatureDataCountryWise.csv")  # read the csv file
df = df.drop("AverageTemperatureUncertainty", axis=1)  # drop the column
df = df.rename(columns={"dt": "Date"})  # rename the column
df = df.rename(columns={"AverageTemperature": "AvTemp"})  # rename the column
df = df.dropna()  # drop the rows with NaN
df_countries = (
    df.groupby(["Country", "Date"])
    .sum()
    .reset_index()
    .sort_values("Date", ascending=False)
)  # group the data by country and date

# Masking by data range
start_date = "2000-01-01"  # start date
end_date = "2002-01-01"  # end date
mask = (df_countries["Date"] > start_date) & (
    df_countries["Date"] <= end_date
)  # mask the data
df_countries = df_countries.loc[mask]

fig = go.Figure(
    data=go.Choropleth(
        locations=df_countries["Country"],
        locationmode="country names",
        z=df_countries["AvTemp"],
        colorscale="Reds",
        marker_line_color="black",
        marker_line_width=0.5,
    )
)
fig.update_layout(
    title_text="Climate Change",
    title_x=0.5,
    geo=dict(showframe=False, showcoastlines=False, projection_type="equirectangular"),
)


# Climate change by timeline
# Manipulating the original dataframe
df_countrydate = df_countries.groupby(["Date", "Country"]).sum().reset_index()
# Creating the visualization
fig2 = px.choropleth(
    df_countrydate,
    locations="Country",
    locationmode="country names",
    color="AvTemp",
    hover_name="Country",
    animation_frame="Date",
)
fig2.update_layout(
    title_text="Average Temperature Change",
    title_x=0.5,
    geo=dict(
        showframe=False,
        showcoastlines=False,
    ),
)


external_stylesheets = ["dash_design.css"]

agg = [
    "Arab World",
    "Caribbean small states",
    "Central Europe and the Baltics",
    "Early-demographic dividend",
    "East Asia & Pacific",
    "East Asia & Pacific (excluding high income)",
    "East Asia & Pacific (IDA & IBRD countries)",
    "Euro area",
    "Europe & Central Asia",
    "Europe & Central Asia (excluding high income)",
    "Europe & Central Asia (IDA & IBRD countries)",
    "European Union",
    "Fragile and conflict affected situations",
    "Heavily indebted poor countries (HIPC)",
    "High income",
    "IBRD only",
    "IDA & IBRD total",
    "IDA blend",
    "IDA only",
    "IDA total",
    "Late-demographic dividend",
    "Latin America & Caribbean",
    "Latin America & Caribbean (excluding high income)",
    "Latin America & the Caribbean (IDA & IBRD countries)",
    "Least developed countries: UN classification",
    "Low & middle income",
    "Low income",
    "Lower middle income",
    "Middle East & North Africa",
    "Middle East & North Africa (excluding high income)",
    "Middle East & North Africa (IDA & IBRD countries)",
    "Middle income",
    "North America",
    "Not classified",
    "OECD members",
    "Other small states",
    "Pacific island small states",
    "Post-demographic dividend",
    "Pre-demographic dividend",
    "Small states",
    "South Asia",
    "South Asia (IDA & IBRD)",
    "Sub-Saharan Africa",
    "Sub-Saharan Africa (excluding high income)",
    "Sub-Saharan Africa (IDA & IBRD countries)",
    "Upper middle income",
    "World",
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# data Cleaning and processing
climateChangeData = "climateChangeData_worldBank.xlsx" # read the csv file
df_dash = pd.read_excel(climateChangeData, na_values="..") 
df_newdash = df_dash.drop(["Country Code", "Series Code"], axis=1) # drop the columns
df_nonagg = df_newdash[-df_newdash["Country Name"].isin(agg)] # drop the rows with aggregated countries
df_flat = df_nonagg.melt(
    id_vars=["Country Name", "Series Name"], var_name="Year", value_name="value"
) # melt the dataframe
df_flat[["Year", "NA"]] = df_flat.Year.str.split(" ", expand=True) # split the year column
df_flat = df_flat.dropna(axis=0, subset=["Country Name"]) # drop the rows with NaN

available_country = df_flat["Country Name"].unique()


# Dash Core Component - Dropdown and Graph is being used where Time-series graph will update based on country selected

#defining the whole layout of the dashboard

# the layouts are in the following order:
# 1. the header
# 2. the subheading
# 3. dropdown menus
# 4. plotly plots of the climateChangeData
# 5. the climate change plot of the World
# 6. the temperature change plot of the World
app.layout = html.Div(
    children=[
        html.H1(
            children="Climate Change Dashboard",
            style={
                "font-family": "monospace",
                "font-size": "50px",
                "textAlign": "center",
                "color": "#874356",
                "backgroundColor": "#FAEDF0",
            },
        ),
        html.Div(
            children="""

      Select two countries from the dropdown menu for comparative study side-by-side
      
      """,
            style={
                "textAlign": "center",
                "font-size": "22px",
                "font-family": "arial",
                "color": "#C65D7B",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id="country1",
                            options=[
                                {"label": i, "value": i} for i in available_country
                            ],
                            value="India",
                            clearable=False,
                        )
                    ],
                    style={
                        "width": "49%",
                        "display": "inline-block",
                        "backgroundColor": "#676FA3",
                    },
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="country2",
                            options=[
                                {"label": i, "value": i} for i in available_country
                            ],
                            value="Japan",
                            clearable=False,
                        )
                    ],
                    style={"width": "49%", "display": "inline-block"},
                ),
            ],
            style={
                "borderBottom": "thin lightgrey solid",
                "backgroundColor": "#676FA3",
                "padding": "10px 5px",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="x-time-series")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                        html.Div(
                            [dcc.Graph(id="y-time-series")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                    ],
                    style={
                        "borderBottom": "thin lightgrey solid",
                        "backgroundColor": "#676FA3",
                        "padding": "10px 5px",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="x-time-series1")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                        html.Div(
                            [dcc.Graph(id="y-time-series1")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                    ],
                    style={
                        "borderBottom": "thin lightgrey solid",
                        "backgroundColor": "#676FA3",
                        "padding": "10px 5px",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="x-time-series2")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                        html.Div(
                            [dcc.Graph(id="y-time-series2")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                    ],
                    style={
                        "borderBottom": "thin lightgrey solid",
                        "backgroundColor": "#676FA3",
                        "padding": "10px 5px",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="x-time-series3")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                        html.Div(
                            [dcc.Graph(id="y-time-series3")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                    ],
                    style={
                        "borderBottom": "thin lightgrey solid",
                        "backgroundColor": "#676FA3",
                        "padding": "10px 5px",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="x-time-series4")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                        html.Div(
                            [dcc.Graph(id="y-time-series4")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                    ],
                    style={
                        "borderBottom": "thin lightgrey solid",
                        "backgroundColor": "#676FA3",
                        "padding": "10px 5px",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="x-time-series5")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                        html.Div(
                            [dcc.Graph(id="y-time-series5")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                    ],
                    style={
                        "borderBottom": "thin lightgrey solid",
                        "backgroundColor": "#676FA3",
                        "padding": "10px 5px",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="x-time-series6")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                        html.Div(
                            [dcc.Graph(id="y-time-series6")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                    ],
                    style={
                        "borderBottom": "thin lightgrey solid",
                        "backgroundColor": "#676FA3",
                        "padding": "10px 5px",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="x-time-series7")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                        html.Div(
                            [dcc.Graph(id="y-time-series7")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                    ],
                    style={
                        "borderBottom": "thin lightgrey solid",
                        "backgroundColor": "#676FA3",
                        "padding": "10px 5px",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="x-time-series8")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                        html.Div(
                            [dcc.Graph(id="y-time-series8")],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                    ],
                    style={
                        "borderBottom": "thin lightgrey solid",
                        "backgroundColor": "#676FA3",
                        "padding": "10px 5px",
                    },
                ),
            ]
        ),
        html.Br(),
        html.Br(),
        html.H1(
            children="World Map Plots ",
            style={
                "font-family": "monospace",
                "font-size": "42px",
                "backgroundColor": "#FAEDF0",
                "textAlign": "center",
                "color": "#874356",
            },
        ),
        html.Br(),
        html.Br(),
        html.Div(
            [dcc.Graph(id="world-map-1", figure=fig)],
            style={
                "width": "90%",
                "display": "inline-block",
                "backgroundColor": "#FAEDF0",
            },
        ),
        html.Br(),
        html.Div(
            [dcc.Graph(id="world-map-2", figure=fig2)],
            style={
                "width": "90%",
                "display": "inline-block",
                "backgroundColor": "#FAEDF0",
            },
        ),
    ]
)


# Define the callback which is responsible for the interactivity in the graph,
# Input value is from the dropdown and output is the time series chart
@app.callback(
    dash.dependencies.Output("x-time-series", "figure"),
    dash.dependencies.Output("y-time-series", "figure"),
    dash.dependencies.Input("country1", "value"),
    dash.dependencies.Input("country2", "value"),
)
# Below code defines the function that will create a dataframe and a time series graph based on country selected in the dropdown.
def update_charts(country1, country2):
    filtered_df = df_flat.loc[df_flat["Country Name"] == country1] # Filter the dataframe based on the country selected in the dropdown

    CO2_df = filtered_df.loc[filtered_df["Series Name"] == "CO2 emissions (kt)"] # Filter the dataframe based on the series name
    maxv = CO2_df.nlargest(1, "value")["value"].values.tolist() # Get the max value from the dataframe
    minv = CO2_df.nsmallest(1, "value")["value"].values.tolist() # Get the min value from the dataframe

    filtered_df2 = df_flat.loc[df_flat["Country Name"] == country2] # Filter the dataframe based on the country selected in the dropdown
    CO2_df2 = filtered_df2.loc[filtered_df2["Series Name"] == "CO2 emissions (kt)"] # Filter the dataframe based on the series name

    maxv2 = CO2_df2.nlargest(1, "value")["value"].values.tolist() # Get the max value from the dataframe
    minv2 = CO2_df2.nsmallest(1, "value")["value"].values.tolist() # Get the min value from the dataframe

    maxva2 = max(maxv + maxv2) # Get the max value from the two countries
    minva2 = min(minv + minv2) # Get the min value from the two countries

    figure1 = px.line(
        CO2_df,
        x="Year",
        y="value",
        title="CO2 emissions (kt)",
        range_y=[minva2, maxva2],
    ) # Create a time series graph based on the CO2 emissions dataframe
    figure2 = px.line(
        CO2_df2,
        x="Year",
        y="value",
        title="CO2 emissions (kt)",
        range_y=[minva2, maxva2],
    ) # Create a time series graph based on the CO2 emissions dataframe
    return figure1, figure2

# similar for other plots Below

@app.callback(
    dash.dependencies.Output("x-time-series1", "figure"),
    dash.dependencies.Output("y-time-series1", "figure"),
    dash.dependencies.Input("country1", "value"),
    dash.dependencies.Input("country2", "value"),
)
# Different code to find min,max values
def update_charts(country1, country2):
    filtered_df = df_flat.loc[df_flat["Country Name"] == country1] # Filtered dataframe for country1

    CO2_df = filtered_df.loc[
        filtered_df["Series Name"] == "Methane emissions (kt of CO2 equivalent)"
    ] # Filtered dataframe for methane emissions
    maxv = CO2_df.nlargest(1, "value")["value"].values.tolist() # Max value for methane emissions
    minv = CO2_df.nsmallest(1, "value")["value"].values.tolist() # Min value for methane emissions

    filtered_df2 = df_flat.loc[df_flat["Country Name"] == country2] # Filtered dataframe for country2
    CO2_df2 = filtered_df2.loc[
        filtered_df2["Series Name"] == "Methane emissions (kt of CO2 equivalent)"
    ] # Filtered dataframe for methane emissions

    maxv2 = CO2_df2.nlargest(1, "value")["value"].values.tolist() # Max value for methane emissions
    minv2 = CO2_df2.nsmallest(1, "value")["value"].values.tolist() # Min value for methane emissions

    maxva2 = max(maxv + maxv2) # Max value for methane emissions
    minva2 = min(minv + minv2)  # Min value for methane emissions

    figure1 = px.line(
        CO2_df,
        x="Year",
        y="value",
        title="Methane emissions (kt of CO2 equivalent)",
        range_y=[minva2, maxva2], 
    ) # Time series graph for methane emissions
    figure2 = px.line(
        CO2_df2,
        x="Year",
        y="value",
        title="Methane emissions (kt of CO2 equivalent)",
        range_y=[minva2, maxva2],
    ) # Time series graph for methane emissions
    return figure1, figure2


@app.callback(
    dash.dependencies.Output("x-time-series2", "figure"),
    dash.dependencies.Output("y-time-series2", "figure"),
    dash.dependencies.Input("country1", "value"),
    dash.dependencies.Input("country2", "value"),
)
# Different code to find min,max values
def update_charts(country1, country2):
    filtered_df = df_flat.loc[df_flat["Country Name"] == country1]

    CO2_df = filtered_df.loc[
        filtered_df["Series Name"]
        == "Total greenhouse gas emissions (kt of CO2 equivalent)"
    ]
    maxv = CO2_df.nlargest(1, "value")["value"].values.tolist()
    minv = CO2_df.nsmallest(1, "value")["value"].values.tolist()

    filtered_df2 = df_flat.loc[df_flat["Country Name"] == country2]
    CO2_df2 = filtered_df2.loc[
        filtered_df2["Series Name"]
        == "Total greenhouse gas emissions (kt of CO2 equivalent)"
    ]

    maxv2 = CO2_df2.nlargest(1, "value")["value"].values.tolist()
    minv2 = CO2_df2.nsmallest(1, "value")["value"].values.tolist()

    maxva2 = max(maxv + maxv2)
    minva2 = min(minv + minv2)

    figure1 = px.line(
        CO2_df,
        x="Year",
        y="value",
        title="GreenHouse gas emissions (kt of CO2 equivalent)",
        range_y=[minva2, maxva2],
    )
    figure2 = px.line(
        CO2_df2,
        x="Year",
        y="value",
        title="GreenHouse gas emissions (kt of CO2 equivalent)",
        range_y=[minva2, maxva2],
    )
    return figure1, figure2


@app.callback(
    dash.dependencies.Output("x-time-series3", "figure"),
    dash.dependencies.Output("y-time-series3", "figure"),
    dash.dependencies.Input("country1", "value"),
    dash.dependencies.Input("country2", "value"),
)
# Different code to find min,max values
def update_charts(country1, country2):
    filtered_df = df_flat.loc[df_flat["Country Name"] == country1]

    CO2_df = filtered_df.loc[
        filtered_df["Series Name"]
        == "Electricity production from oil, gas and coal sources (% of total)"
    ]
    maxv = CO2_df.nlargest(1, "value")["value"].values.tolist()
    minv = CO2_df.nsmallest(1, "value")["value"].values.tolist()

    filtered_df2 = df_flat.loc[df_flat["Country Name"] == country2]
    CO2_df2 = filtered_df2.loc[
        filtered_df2["Series Name"]
        == "Electricity production from oil, gas and coal sources (% of total)"
    ]

    maxv2 = CO2_df2.nlargest(1, "value")["value"].values.tolist()
    minv2 = CO2_df2.nsmallest(1, "value")["value"].values.tolist()

    maxva2 = max(maxv + maxv2)
    minva2 = min(minv + minv2)

    figure1 = px.line(
        CO2_df,
        x="Year",
        y="value",
        title="Electricity production from oil, gas and coal sources",
        range_y=[minva2, maxva2],
    )
    figure2 = px.line(
        CO2_df2,
        x="Year",
        y="value",
        title="Electricity production from oil, gas and coal sources",
        range_y=[minva2, maxva2],
    )
    return figure1, figure2


@app.callback(
    dash.dependencies.Output("x-time-series4", "figure"),
    dash.dependencies.Output("y-time-series4", "figure"),
    dash.dependencies.Input("country1", "value"),
    dash.dependencies.Input("country2", "value"),
)
# Below code defines the function that will create a dataframe and a time series graph based on country selected in the dropdown.
def update_charts(country1, country2):
    filtered_df = df_flat.loc[df_flat["Country Name"] == country1]

    CO2_df = filtered_df.loc[
        filtered_df["Series Name"]
        == "Electricity production from renewable sources, excluding hydroelectric (kWh)"
    ]
    maxv = CO2_df.nlargest(1, "value")["value"].values.tolist()
    minv = CO2_df.nsmallest(1, "value")["value"].values.tolist()

    filtered_df2 = df_flat.loc[df_flat["Country Name"] == country2]
    CO2_df2 = filtered_df2.loc[
        filtered_df2["Series Name"]
        == "Electricity production from renewable sources, excluding hydroelectric (kWh)"
    ]

    maxv2 = CO2_df2.nlargest(1, "value")["value"].values.tolist()
    minv2 = CO2_df2.nsmallest(1, "value")["value"].values.tolist()

    maxva2 = max(maxv + maxv2)
    minva2 = min(minv + minv2)

    figure1 = px.line(
        CO2_df,
        x="Year",
        y="value",
        title="Electricity production from renewable sources, excluding hydroelectric (kWh)",
        range_y=[minva2, maxva2],
    )
    figure2 = px.line(
        CO2_df2,
        x="Year",
        y="value",
        title="Electricity production from renewable sources, excluding hydroelectric (kWh)",
        range_y=[minva2, maxva2],
    )
    return figure1, figure2


@app.callback(
    dash.dependencies.Output("x-time-series5", "figure"),
    dash.dependencies.Output("y-time-series5", "figure"),
    dash.dependencies.Input("country1", "value"),
    dash.dependencies.Input("country2", "value"),
)
# Below code defines the function that will create a dataframe and a time series graph based on country selected in the dropdown.
def update_charts(country1, country2):
    filtered_df = df_flat.loc[df_flat["Country Name"] == country1]

    CO2_df = filtered_df.loc[
        filtered_df["Series Name"]
        == "Other greenhouse gas emissions, HFC, PFC and SF6 (thousand metric tons of CO2 equivalent)"
    ]
    maxv = CO2_df.nlargest(1, "value")["value"].values.tolist()
    minv = CO2_df.nsmallest(1, "value")["value"].values.tolist()

    filtered_df2 = df_flat.loc[df_flat["Country Name"] == country2]
    CO2_df2 = filtered_df2.loc[
        filtered_df2["Series Name"]
        == "Other greenhouse gas emissions, HFC, PFC and SF6 (thousand metric tons of CO2 equivalent)"
    ]

    maxv2 = CO2_df2.nlargest(1, "value")["value"].values.tolist()
    minv2 = CO2_df2.nsmallest(1, "value")["value"].values.tolist()

    maxva2 = max(maxv + maxv2)
    minva2 = min(minv + minv2)

    figure1 = px.line(
        CO2_df,
        x="Year",
        y="value",
        title="Other greenhouse gas emissions, HFC, PFC and SF6",
        range_y=[minva2, maxva2],
    )
    figure2 = px.line(
        CO2_df2,
        x="Year",
        y="value",
        title="Other greenhouse gas emissions, HFC, PFC and SF6",
        range_y=[minva2, maxva2],
    )
    return figure1, figure2


@app.callback(
    dash.dependencies.Output("x-time-series6", "figure"),
    dash.dependencies.Output("y-time-series6", "figure"),
    dash.dependencies.Input("country1", "value"),
    dash.dependencies.Input("country2", "value"),
)
# Below code defines the function that will create a dataframe and a time series graph based on country selected in the dropdown.
def update_charts(country1, country2):
    filtered_df = df_flat.loc[df_flat["Country Name"] == country1]

    CO2_df = filtered_df.loc[
        filtered_df["Series Name"]
        == "Total greenhouse gas emissions (kt of CO2 equivalent)"
    ]
    maxv = CO2_df.nlargest(1, "value")["value"].values.tolist()
    minv = CO2_df.nsmallest(1, "value")["value"].values.tolist()

    filtered_df2 = df_flat.loc[df_flat["Country Name"] == country2]
    CO2_df2 = filtered_df2.loc[
        filtered_df2["Series Name"]
        == "Total greenhouse gas emissions (kt of CO2 equivalent)"
    ]

    maxv2 = CO2_df2.nlargest(1, "value")["value"].values.tolist()
    minv2 = CO2_df2.nsmallest(1, "value")["value"].values.tolist()

    maxva2 = max(maxv + maxv2)
    minva2 = min(minv + minv2)

    figure1 = px.line(
        CO2_df,
        x="Year",
        y="value",
        title="Total greenhouse gas emissions (kt of CO2 equivalent)",
        range_y=[minva2, maxva2],
    )
    figure2 = px.line(
        CO2_df2,
        x="Year",
        y="value",
        title="Total greenhouse gas emissions (kt of CO2 equivalent)",
        range_y=[minva2, maxva2],
    )
    return figure1, figure2


@app.callback(
    dash.dependencies.Output("x-time-series7", "figure"),
    dash.dependencies.Output("y-time-series7", "figure"),
    dash.dependencies.Input("country1", "value"),
    dash.dependencies.Input("country2", "value"),
)
# Below code defines the function that will create a dataframe and a time series graph based on country selected in the dropdown.
def update_charts(country1, country2):
    filtered_df = df_flat.loc[df_flat["Country Name"] == country1]

    CO2_df = filtered_df.loc[
        filtered_df["Series Name"]
        == "Population density (people per sq. km of land area)"
    ]
    maxv = CO2_df.nlargest(1, "value")["value"].values.tolist()
    minv = CO2_df.nsmallest(1, "value")["value"].values.tolist()

    filtered_df2 = df_flat.loc[df_flat["Country Name"] == country2]
    CO2_df2 = filtered_df2.loc[
        filtered_df2["Series Name"]
        == "Population density (people per sq. km of land area)"
    ]

    maxv2 = CO2_df2.nlargest(1, "value")["value"].values.tolist()
    minv2 = CO2_df2.nsmallest(1, "value")["value"].values.tolist()

    maxva2 = max(maxv + maxv2)
    minva2 = min(minv + minv2)

    figure1 = px.line(
        CO2_df,
        x="Year",
        y="value",
        title="Population density (people per sq. km of land area)",
        range_y=[minva2, maxva2],
    )
    figure2 = px.line(
        CO2_df2,
        x="Year",
        y="value",
        title="Population density (people per sq. km of land area)",
        range_y=[minva2, maxva2],
    )
    return figure1, figure2


@app.callback(
    dash.dependencies.Output("x-time-series8", "figure"),
    dash.dependencies.Output("y-time-series8", "figure"),
    dash.dependencies.Input("country1", "value"),
    dash.dependencies.Input("country2", "value"),
)
# Below code defines the function that will create a dataframe and a time series graph based on country selected in the dropdown.
def update_charts(country1, country2):
    filtered_df = df_flat.loc[df_flat["Country Name"] == country1]

    CO2_df = filtered_df.loc[
        filtered_df["Series Name"] == "Fossil fuel energy consumption (% of total)"
    ]
    maxv = CO2_df.nlargest(1, "value")["value"].values.tolist()
    minv = CO2_df.nsmallest(1, "value")["value"].values.tolist()

    filtered_df2 = df_flat.loc[df_flat["Country Name"] == country2]
    CO2_df2 = filtered_df2.loc[
        filtered_df2["Series Name"] == "Fossil fuel energy consumption (% of total)"
    ]

    maxv2 = CO2_df2.nlargest(1, "value")["value"].values.tolist()
    minv2 = CO2_df2.nsmallest(1, "value")["value"].values.tolist()

    maxva2 = max(maxv + maxv2)
    minva2 = min(minv + minv2)

    figure1 = px.line(
        CO2_df,
        x="Year",
        y="value",
        title="Fossil fuel energy consumption (% of total)",
        range_y=[minva2, maxva2],
    )
    figure2 = px.line(
        CO2_df2,
        x="Year",
        y="value",
        title="Fossil fuel energy consumption (% of total)",
        range_y=[minva2, maxva2],
    )
    return figure1, figure2


if __name__ == "__main__": # This code is executed only when the file is run directly.
    app.run_server(debug=True, use_reloader=False)  # Run the app in debug mode.
