import os
import requests
import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px

dash.register_page(__name__, path='/', title="ExploreU")

topics_path = os.getcwd() + dash.get_asset_url("data/query_terms.csv")
pdf_path = os.getcwd() + dash.get_asset_url("data/full_bach_pdf.csv")

topics = list(pd.read_csv(topics_path)['0'])
pdf_data = pd.read_csv(pdf_path, dtype={"cip_code": str, "year": int})

search = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.I(className="fa-solid fa-circle-info"),
                                    html.P(
                                        '''Pick topics of interest in order.''',
                                        className='info',
                                        style={'width': '13rem'}
                                    )
                                ],
                                className="tooltip"
                            ),
                            width=1
                        ),
                        dbc.Col(dcc.Dropdown(topics, placeholder="Topic #1", id="topics-1")),
                        dbc.Col(dcc.Dropdown(topics, placeholder="Topic #2", id="topics-2")),
                        dbc.Col(dcc.Dropdown(topics, placeholder="Topic #3", id="topics-3")),
                        dbc.Col(dcc.Dropdown(topics, placeholder="Topic #4", id="topics-4")),
                        dbc.Col(dcc.Dropdown(topics, placeholder="Topic #5", id="topics-5"))
                    ],
                    className="g-1",
                ),
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
    style={'width': '900px'}
)

results_container = dbc.Col(
    [
        html.P(id="cip-count"),
        html.Div(id="cip-results")
    ]
)

viz_container = dbc.Col(
    [
        html.Div(
            [
                dcc.Graph(id="salary-viz")
            ],
            id="viz-container"
        ),
    ],
    style={'visibility': 'hidden'}
)

layout = dbc.Container([
    html.Br(),
    search,
    html.Br(),
    dbc.Row(
        [
            dbc.Col(dcc.Loading(results_container, type="circle", color="#158cba")),
            dbc.Col(dcc.Loading(viz_container, type="circle", color="#158cba"))
        ]
    )
])

@dash.callback(
    [
        Output('results-temp', 'data'),
        Output('cip-count', 'children'),
        Output('viz-container', 'style')
    ],
    Input('search-button', 'n_clicks'),
    [
        State('topics-1', 'value'),
        State('topics-2', 'value'),
        State('topics-3', 'value'),
        State('topics-4', 'value'),
        State('topics-5', 'value')
    ],
    prevent_initial_call=True
)
def update_results(click, topic1, topic2, topic3, topic4, topic5):
    # retrieve results from model here
    # cip_results = ["45.06", "30.70", "11.01", "13.06", "11.07"]
    url = f"http://127.0.0.1:8000/topics/{topic1}+{topic2}+{topic3}+{topic4}+{topic5}"
    cip_results = requests.get(url).json()['cips']
    cip_path = os.getcwd() + dash.get_asset_url("data/cip_url_summary.csv")
    cip_info = pd.read_csv(cip_path, dtype={"CIPCode": str})

    cips = list(cip_info['CIPCode'])
    results = []
    for cip in cip_results:
        if cip in cips:
            related = cip_info.loc[cip_info['CIPCode'] == cip, "related"].item().split(",")
            related_ls = []
            for i in related:
                if i in cips:
                    related_ls.append(
                        {
                            "cip": i,
                            "title": cip_info.loc[cip_info['CIPCode'] == i, "CIPTitle"].item()[:-1],
                            "url": cip_info.loc[cip_info['CIPCode'] == i, "url"].item()
                        }
                    )
            results.append({
                "cip": cip,
                "name": cip_info.loc[cip_info['CIPCode'] == cip, "CIPTitle"].item()[:-1],
                "related": related_ls,
                "description": cip_info.loc[cip_info['CIPCode'] == cip, "CIPDefinition_summary"].item(),
                "url": cip_info.loc[cip_info['CIPCode'] == cip, "url"].item()
            })

    n_results = f"Returning top {len(results)} matches"

    return results, n_results, {'visibility': 'visible'}

@dash.callback(
    Output('cip-results', 'children'),
    Input('results-temp', 'data'),
    prevent_initial_call=True
)
def display_cards(data):
    cards = []
    for cip in data:
        cards.append(generate_card(cip))
        cards.append(html.Br())

    return cards

def generate_card(data):
    card = dbc.Card(
        [
            dbc.CardHeader(html.A(f"CIP {data['cip']}", href=data['url'], target="_blank")),
            dbc.CardBody(
                [
                    html.H4(data['name'], className="card-title"),
                    html.P(data['description'], className="card-text"),
                    html.Div(generate_labels(data['related']), className="card-text")
                ]
            )
        ]
    )

    return card

def generate_labels(data):
    labels = []
    if len(data) > 0:
        for cip in data:
            labels.append(html.Span(html.A(cip['cip'], href=cip['url'], title=cip['title'], target="_blank")))
    return labels


@dash.callback(
    Output('salary-viz', 'figure'),
    Input('results-temp', 'data'),
    prevent_initial_call=True
)
def plot_salary(data):
    cip_list = [i['cip'] for i in data]
    fig_data = pdf_data[pdf_data['cip_code'].isin(cip_list)]
    fig = px.line(
        fig_data, x='year', y='mean_starting_salary', color='cip_code',
        labels={'year': '', 'mean_starting_salary': '', 'cip_code': "CIP"}, template="ggplot2"
    )
    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(hovermode="x unified", title={'text': "Mean Starting Salary", 'y': 0.95}, height=400)
    
    return fig