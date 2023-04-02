import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import os

dash.register_page(__name__, path='/', title="ExploreU")

topics = ['Math', 'Linguistics', 'History', 'Politics', 'Gaming', 'Music']

search = dbc.Row(
    [
        dbc.Col(
            [
                dcc.Dropdown(topics, value=[], persistence=True, multi=True, placeholder="Select topics in order", id="topics"),
                dcc.Store(id='results-temp'),
            ]
        ),
        dbc.Col(
            dbc.Button(
                "Search", color="secondary", class_name="ms-2",
                id="search-button", n_clicks=0
            ),
            width="auto"
        )
    ],
    class_name="g-2 ms-auto flex-wrap mx-auto",
    align="center",
    justify="center",
    style={'width': '800px'}
)

results_container = dbc.Col(
    [
        html.P(id="cip-count"),
        html.Div(id="cip-results")
    ]
)

viz_container = dbc.Col(
    [
        html.Div(id="viz-container")
    ]
)

layout = dbc.Container([
    html.Br(),
    search,
    html.Br(),
    dbc.Row(
        [
            dbc.Col(results_container),
            dbc.Col(viz_container)
        ]
    )
])

@dash.callback(
    [
        Output('results-temp', 'data'),
        Output('cip-count', 'children')
    ],
    Input('search-button', 'n_clicks'),
    State('topics', 'value')
)
def update_results(click, topics):
    # retrieve results from model here
    cip_results = ["45.06", "30.70", "11.01", "13.06"]
    cip_path = os.getcwd() + dash.get_asset_url("data/cip_url_summary.csv")
    cip_info = pd.read_csv(cip_path, dtype={"CIPCode": str})

    cips = list(cip_info['CIPCode'])
    results = [{
        "cip": cip,
        "name": cip_info.loc[cip_info['CIPCode'] == cip, "CIPTitle"].item()[:-1],
        "related": cip_info.loc[cip_info['CIPCode'] == cip, "related"].item(),
        "description": cip_info.loc[cip_info['CIPCode'] == cip, "CIPDefinition_summary"].item(),
        "url": cip_info.loc[cip_info['CIPCode'] == cip, "url"].item()
    } for cip in cip_results if cip in cips]

    n_results = f"Returning top {len(results)} matches"

    return results, n_results

@dash.callback(
    Output('cip-results', 'children'),
    Input('results-temp', 'data')
)
def display_cards(data):
    cards = []
    for cip in data:
        cards.append(generate_card(cip))
        cards.append(html.Br())

    return cards

def generate_card(data):
    related = data['related'].split(',')
    card = dbc.Card(
        [
            dbc.CardHeader(html.A(f"CIP {data['cip']}", href=data['url'], target="_blank")),
            dbc.CardBody(
                [
                    html.H4(data['name'], className="card-title"),
                    html.P(data['description'], className="card-text"),
                    html.Div([html.Span(related[0]), html.Span(related[1]), html.Span(related[2])] if len(related) > 0 else [])
                ]
            )
        ]
    )

    return card