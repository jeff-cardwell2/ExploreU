import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

dash.register_page(__name__, path='/', title="ExploreU")

topics = ['Math', 'Linguistics', 'History', 'Politics', 'Gaming', 'Music']

search = dbc.Row(
    [
        html.Br(),
        dbc.Col(
            [
                html.Br(),
                dcc.Dropdown(topics, value=[], persistence=True, multi=True, placeholder="Select topics in order", id="topics")
            ]
        )
    ],
    class_name="g-2 ms-auto flex-wrap mx-auto",
    align="center",
    justify="center",
    style={'width': '800px'}
)

results_container = dbc.Container(
    [
        dbc.Col()
    ]
)

viz_container = dbc.Container(
    [
        dbc.Col()
    ]
)

layout = dbc.Container([
    search
])