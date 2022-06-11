#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


@author: VK
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
import requests

import pandas as pd


import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash import ctx
from dash.dependencies import Output, Input, State
import plotly.express as px
import plotly.io as pio

pio.renderers.default = "browser"


# BIKE_URL = "https://api.tfl.gov.uk/BikePoint/BikePoints_"
BIKE_URL = "https://api.tfl.gov.uk/BikePoint/"
TUBE_URL = "http://cloud.tfl.gov.uk/TrackerNet/LineStatus"


def static_data(fname: str) -> pd.DataFrame:
    """
    Read static dock data from CSV file

    Parameters
    ----------
    fname : str
        filepath of the CSV file.

    Returns
    -------
    stations_static : pd.DataFrame
        A DataFrame containing the dock info.

    """
    stations_static = pd.read_csv(fname)
    
    return stations_static


stations_df = static_data('stations_static.csv').sort_values('Name')

def tube_status():
    """
    Fetch live Tube, DLR, Elizabeth and Tram status

    Returns
    -------
    result : List[Dict]
        Returns a list of dictionaries {'Line': Name, 'Status': status}

    """

    r = requests.get(TUBE_URL)    
    root = ET.fromstring(r.text[3:])    
    result = []
    
    for child in root:
        d = {
            'Line': child[1].attrib['Name'],
            'Status': child[2].attrib['Description']
            }
        
        result.append(d)
        
    return result

tubes = tube_status()


@dataclass
class Station:
    ident: str
    name: str = field(init=False)
    lat: float = field(init=False)
    lon: float = field(init=False)
    nbikes: int = field(init=False)
    nempty: int = field(init=False)
    ts: pd.Timestamp = field(init=False)
    
    def __post_init__(self):
        r = requests.get(BIKE_URL + str(self.ident))
        dockinfo = r.json()
        self.name = dockinfo['commonName']
        self.lat = dockinfo['lat']
        self.lon = dockinfo['lon']
        self.nbikes = dockinfo['additionalProperties'][6]['value']
        self.nempty = dockinfo['additionalProperties'][7]['value']
        self.ts = (pd.Timestamp(
            dockinfo['additionalProperties'][7]['modified'])
            .tz_convert('Europe/London'))
        
    def to_dataframe(self):
        df = pd.DataFrame(columns=[
            'ID', 'Name', 'Bikes', 'Spaces', 'Lat', 'Lon', 'Date', 'Time',
            'hover'])
        df['ID'] = [self.ident]
        df['Name'] = [self.name]
        df['Bikes'] = [self.nbikes]
        df['Spaces'] = [self.nempty]
        df['Lat'] = [self.lat]
        df['Lon'] = [self.lon]
        df['Date'] = [self.ts.strftime('%a %-d %b')]
        df['Time'] = [self.ts.strftime('%H:%M:%S')]
        df['hover'] = ['{bikes} Bikes\n{spaces} Spaces\nat {time}'
                       .format(bikes=self.nbikes,
                               spaces=self.nempty,
                               time=self.ts.strftime('%H:%M:%S'))]
        return df
        
    def to_dict(self):
        dic = dict(ID=self.ident,
                   Name=self.name,
                   Bikes=self.nbikes,
                   Spaces=self.nempty,
                   Date=self.ts.strftime('%a %-d %b'),
                   Time=self.ts.strftime('%H:%M:%S'))
        return dic
        
        
# stns = [Station(s) for s in stations]
# _ = [s.to_dict() for s in stns]
# data = [Station(s).to_dict() for s in stations]
# data_df = pd.concat(
#     [Station(s).to_dataframe() for s in stations], ignore_index=True)


"""
Dash section
"""


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


app.title = "VK Commute Status"

bike_tblcols = ['Name', 'Bikes', 'Spaces', 'Date', 'Time']
tube_tblcols = ['Line', 'Status']

dock_options = [
    {"label": dock[0], "value": dock[1]}
    for _, dock in stations_df.iterrows()]

lines = [t['Line'] for t in tubes]
tube_options = [
    {"label": line, "value": line}
    for line in lines]

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🚲", className="header-emoji"),
                html.H1(
                    children="VK Commute Status", className="header-title"
                ),
                html.P(
                    children="""Check line status and 
                    availability of bikes and spaces""",
                    className="header-description",
                ),
                ],
            className="header"
            ),
        
        html.Div(
            children=html.P(
                children="Select line(s)", className="menu-title")
            ),
        
        html.Div(
            children=[
                # html.Div(children="Dock 1", className="menu-title"),
                html.Div(
                    children=dcc.Dropdown(
                        id="lines",
                        options=tube_options,
                        value=['DLR',
                               'Elizabeth',
                               'Jubilee',
                               'Central'
                               ],
                        multi=True,
                        clearable=True,
                        className="dropdown",
                        ),
                    ),
                ],
            className="menu",
            ),
        
        html.Div(
            children=html.Button('Refresh', id='refresh_line'),
            className="button"
            ),
        
        html.Div(
            children=[
                dash_table.DataTable(
                    id='lines-table',
                    # data=data,
                    columns=[
                        {"name": k, "id": k} for k in tube_tblcols],
                    style_as_list_view=True,
                    style_cell={
                        'padding': '5px',
                        'textAlign': 'center'
                        },
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'center'
                        },
                    style_data_conditional=[
                        {
                            'if': {
                                'filter_query': "{Status} != 'Good Service'", 
                                # 'column_id': 'Status'
                                },
                            'backgroundColor': 'tomato',
                            'color': 'white'
                            }
                        ]
                    )
                ],
            className="table"
            ),
        
        
        
        html.Div(
            children=html.P(
                children="Select dock(s)", className="menu-title")
            ),
        
        html.Div(
            children=[
                # html.Div(children="Dock 1", className="menu-title"),
                html.Div(
                    children=dcc.Dropdown(
                        id="docks",
                        options=dock_options,
                        value=['BikePoints_109',
                               'BikePoints_244',
                               'BikePoints_141',
                               'BikePoints_301',
                               'BikePoints_106'],
                        multi=True,
                        clearable=True,
                        className="dropdown",
                        ),
                    ),
                ],
            className="menu",
            ),
        
        html.Div(
            children=html.Button('Refresh', id='refresh_dock'),
            className="button"
            ),
           
        html.Div(
            children=[
                dash_table.DataTable(
                    id='stations-table',
                    # data=data,
                    columns=[
                        {"name": k, "id": k} for k in bike_tblcols],
                    style_as_list_view=True,
                    style_cell={
                        'padding': '5px',
                        'textAlign': 'center'
                        },
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'center'
                        },
                    )
                ],
            className="table"
            ),
        
        html.Div(
            children=[
                ])
        ]
    )

 
@app.callback(
    Output('lines-table', 'data'),
    # Output('refresh_dock', 'n_clicks'),
    Input('refresh_line', 'n_clicks'),
    Input('lines', 'value'))
def refresh_tube_table(clicks, lines):
    if ctx.triggered is not None:
        # clicks = 0
        if isinstance(lines, list):
            data = [t for t in tube_status() if t['Line'] in lines]
        elif isinstance(lines, str):
            data = [t for t in tube_status() if t['Line']==lines]
        else:
            data = []
    
    return data #, clicks

   
@app.callback(
    Output('stations-table', 'data'),
    # Output('refresh_dock', 'n_clicks'),
    Input('refresh_dock', 'n_clicks'),
    Input('docks', 'value'))
def refresh_dock_table(clicks, docks):
    if ctx.triggered is not None:
        # clicks = 0
        if isinstance(docks, list):
            data = [Station(s).to_dict() for s in docks]
        elif isinstance(docks, str):
            data = [Station(docks).to_dict()]
        else:
            data = []
    
    return data #, clicks

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port='8050')
        
