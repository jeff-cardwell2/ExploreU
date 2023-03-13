import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

dash.register_page(__name__, path='/')

layout = dbc.Container()