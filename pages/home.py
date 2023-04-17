import os
import requests
import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

dash.register_page(__name__, path='/', title="ExploreU")

topics_path = os.getcwd() + dash.get_asset_url("data/query_terms.csv")
pdf_path = os.getcwd() + dash.get_asset_url("data/pdf_merged.csv")
cip_path = os.getcwd() + dash.get_asset_url("data/cip_url_summary.csv")
sc_path = os.getcwd() + dash.get_asset_url("data/scorecard_merged.csv")

topics = sorted(list(pd.read_csv(topics_path)['0']))
pdf_data = pd.read_csv(pdf_path, index_col=0, dtype={'cip_code': str, 'CIPCode': str, "year": int})
cip_info = pd.read_csv(cip_path, dtype={"CIPCode": str})
sc_data = pd.read_csv(sc_path, index_col=0, dtype={'cip_code': str, 'CIPCode': str})

colors = ["#F8766D", "#D89000", "#A3A500", "#39B600", "#00BF7D", "#00BFC4", "#00B0F6", "#9590FF", "#E76BF3", "#FF62BC"]

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
                        dbc.Col(dcc.Dropdown(topics, persistence=True, placeholder="Topic #1", id="topics-1")),
                        dbc.Col(dcc.Dropdown(topics, persistence=True, placeholder="Topic #2", id="topics-2")),
                        dbc.Col(dcc.Dropdown(topics, persistence=True, placeholder="Topic #3", id="topics-3")),
                        dbc.Col(dcc.Dropdown(topics, persistence=True, placeholder="Topic #4", id="topics-4")),
                        dbc.Col(dcc.Dropdown(topics, persistence=True, placeholder="Topic #5", id="topics-5"))
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
                dcc.Graph(id="salary-viz"),
                dcc.Graph(id="employment-viz"),
                dcc.Graph(id="nyear-viz"),
                dcc.Graph(id="gender-viz")
            ],
            id="viz-container",
            style={'display': 'none'}
        ),
    ]
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
    url = f"https://qkljp7mtn5hed6ctzqsntgbqom0tbdgm.lambda-url.us-east-1.on.aws/topics/{topic1}+{topic2}+{topic3}+{topic4}+{topic5}"
    cip_results = requests.get(url).json()['cips']

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

    return results, n_results, {'display': 'block'}

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
    salary = go.Figure()
    
    for i, cip in enumerate(cip_list):
        cip_data = fig_data[fig_data['cip_code'] == cip].sort_values(by=['year'])
        if len(cip_data) > 0:
            cip_data['cip_upper'] = cip_data['mean_starting_salary'] + 500
            cip_data['cip_lower'] = cip_data['mean_starting_salary'] - 500
            cip_title = cip_data.iloc[0]['CIPTitle']
            
            year_bounds = list(cip_data['year']) + list(cip_data['year'])[::-1]
            salary_bounds = list(cip_data['cip_upper']) + list(cip_data['cip_lower'])[::-1]
            
            salary.add_trace(
                go.Scatter(
                    name=cip_title,
                    x=year_bounds,
                    y=salary_bounds,
                    mode='lines',
                    hoverinfo='name',#"%{name}<extra></extra>",
                    fill='toself',
                    fillcolor=colors[i],
                    line_color=colors[i],
                    showlegend=False,
                    opacity=0.25
                )
            )
            
            salary.add_trace(
                go.Scatter(
                    name=cip,
                    x=cip_data['year'],
                    y=cip_data['mean_starting_salary'].round(-3),
                    mode='lines+markers',
                    line_color=colors[i],
                    hovertext=cip_data['CIPTitle'],
                    hovertemplate="<b>%{hovertext}</b><br><br>"+"Year: %{x}<br>"+"Mean Starting Salary: $%{y}<br>"+"<extra></extra>"
                )
            )
    
    salary.update_layout(
        template='ggplot2', legend_title='CIP Code', hoverlabel=dict(namelength=-1),
        title={'text': "Mean Starting Salary", 'y': 0.85}, height=400
    )
    
    return salary


@dash.callback(
    Output('employment-viz', 'figure'),
    Input('results-temp', 'data'),
    prevent_initial_call=True
)
def plot_employment(data):
    cip_list = [i['cip'] for i in data]
    fig_data = pdf_data[pdf_data['cip_code'].isin(cip_list)]
    grouped = fig_data.groupby('cip_code').mean(numeric_only=True).reset_index()
    grouped = grouped.merge(fig_data[['CIPCode', 'CIPTitle']], how='left', left_on='cip_code', right_on='CIPCode')
    grouped.drop_duplicates(inplace=True)
    
    # selected_grouped = grouped[grouped['cip_code'].isin(selected_cips)]
    # other_grouped = grouped[~grouped['cip_code'].isin(selected_cips)]
    # if len(selected_grouped) == 0:
    #     opacity = 1.0
    # else:
    #     opacity = 0.25
    
    stacked = go.Figure(
        data=[
            go.Bar(
                name='Percent Employed',
                x=grouped['cip_code'],
                y=grouped['total_perc_employed_overall'],
                marker_color=colors[4],
                hovertext=grouped['CIPTitle'],
                hovertemplate="<b>%{hovertext}</b><br><br>"+"Percent Employed: %{y:.0f}%<br>"+"<extra></extra>"
            ),                     
            go.Bar(
                name='Percent Continuing Education',
                x=grouped['cip_code'],
                y=grouped['perc_continuing_ed'],
                marker_color=colors[6],
                hovertext=grouped['CIPTitle'],
                hovertemplate="Percent Continuing Education: %{y:.0f}%<br>"+"<extra></extra>"
            ),
            #   go.Bar(name='Percent Employed',
            #         x=other_grouped['cip_code'],
            #         y=other_grouped['total_perc_employed_overall'],
            #         opacity = opacity,
            #         hovertext = other_grouped['CIPTitle'],
            #         hovertemplate = "<b>%{hovertext}</b><br><br>" +
            #          "Percent Employed: %{y:.0f}%<br>"+"<extra></extra>"),
                
            #   go.Bar(name='Percent Continuing Education',
            #         x=other_grouped['cip_code'],
            #         y=other_grouped['perc_continuing_ed'],
            #         opacity = opacity,
            #         hovertext = other_grouped['CIPTitle'],
            #         hovertemplate =  
            #          "Percent Continuing Education: %{y:.0f}%<br>"+"<extra></extra>")
        ]
    )
    
    stacked.update_layout(
        barmode='stack', title='Average First-Year Outcomes by CIP Code',
        xaxis_title='CIP Code', yaxis_title='Percentage',
        hovermode='x unified', template='ggplot2', height=400,
        legend={'traceorder':'normal', 'borderwidth':1, 'yanchor':'middle', 'y':1.02, 'xanchor':'right', 'x':0.99}
    )
    
    return stacked


@dash.callback(
    Output('nyear-viz', 'figure'),
    Input('results-temp', 'data'),
    prevent_initial_call=True
)
def plot_nyear(data):
    cip_list = [i['cip'] for i in data]
    fig_data = sc_data[sc_data['cip_code'].isin(cip_list)]
    # selected_grouped = fig_data[fig_data['cip_code'].isin(selected_cips)]
    # other_grouped = fig_data[~fig_data['cip_code'].isin(selected_cips)]
    # if len(selected_grouped) == 0:
    #     opacity = 1.0
    # else:
    #     opacity = 0.25

    grouped = go.Figure(
        data=[
            go.Bar(
                name='1-Year Median Earnings',
                x=fig_data['cip_code'],
                y=fig_data['earnings.highest.1_yr.overall_median_earnings'].round(-3),
                marker_color=colors[4],
                hovertext=fig_data['CIPTitle'],
                hovertemplate="<b>%{hovertext}</b><br><br>"+
                    "1-Year Median Earnings: $%{y}<br>"+"<extra></extra>"
            ),                   
            go.Bar(
                name='2-Year Median Earnings',
                x=fig_data['cip_code'],
                y=fig_data['earnings.highest.2_yr.overall_median_earnings'].round(-3),
                marker_color=colors[6],
                hovertext=fig_data['CIPTitle'],
                hovertemplate="<b>%{hovertext}</b><br><br>"+
                "2-year Median Earnings: $%{y}<br>"+"<extra></extra>"
            ),
                              
            #   go.Bar(name='1-Year Median Earnings',
            #         x=other_grouped['cip_code'],
            #         y=other_grouped['earnings.highest.1_yr.overall_median_earnings'].round(-3),
            #         opacity = opacity,
            #         hovertext = other_grouped['CIPTitle'],
            #         hovertemplate = "<b>%{hovertext}</b><br><br>" +
            #          "1-Year Median Earnings: $%{y}<br>"+"<extra></extra>"),
                
            #   go.Bar(name='2-Year Median Earnings',
            #         x=other_grouped['cip_code'],
            #         y=other_grouped['earnings.highest.2_yr.overall_median_earnings'].round(-3),
            #         opacity = opacity,
            #         hovertext = other_grouped['CIPTitle'],
            #         hovertemplate = "<b>%{hovertext}</b><br><br>" +
            #          "2-Year Median Earnings: $%{y}<br>"+"<extra></extra>")
        ]
    )
    grouped.update_layout(
        barmode='group', title='First and Second Year Post-Grad Median Earnings by CIP Code',
        xaxis_title='CIP Code', yaxis_title='Reported Post-Grad Earnings',
        template='ggplot2', height=400,
        legend={'traceorder':'normal', 'borderwidth':1, 'yanchor':'middle', 'y':1.02, 'xanchor':'right', 'x':0.99})
    
    return grouped


@dash.callback(
    Output('gender-viz', 'figure'),
    Input('results-temp', 'data'),
    prevent_initial_call=True
)
def plot_gender(data):
    cip_list = [i['cip'] for i in data]
    fig_data = sc_data[sc_data['cip_code'].isin(cip_list)]
    
    # selected_grouped = fig_data[fig_data['cip_code'].isin(selected_cips)]
    # other_grouped = fig_data[~fig_data['cip_code'].isin(selected_cips)]
    # if len(selected_grouped) == 0:
    #     opacity = 1.0
    # else:
    #     opacity = 0.25
    
    grouped = go.Figure(
        data=[
            go.Bar(
                name='1-Year Nonmale Median Earnings',
                x=fig_data['CIPCode'],
                y=fig_data['earnings.highest.1_yr.nonmale_median_earnings'].round(-3),
                marker_color=colors[4],
                hovertext=fig_data['CIPTitle'],
                hovertemplate="<b>%{hovertext}</b><br><br>"+"Median Nonmale Earnings: $%{y}<br>"+"<extra></extra>"
            ),                  
            go.Bar(
                name='1-Year Male Median Earnings',
                x=fig_data['CIPCode'],
                y=fig_data['earnings.highest.1_yr.male_median_earnings'].round(-3),
                marker_color=colors[6],
                hovertext=fig_data['CIPTitle'],
                hovertemplate="<b>%{hovertext}</b><br><br>"+"Median Male Earnings: $%{y}<br>"+"<extra></extra>"
            ),

            #   go.Bar(name='1-Year Nonmale Median Earnings',
            #         x=other_grouped['cip_code'],
            #         y=other_grouped['earnings.highest.1_yr.nonmale_median_earnings'].round(-3),
            #         opacity = opacity,
            #         hovertext = other_grouped['CIPTitle'],
            #         hovertemplate = "<b>%{hovertext}</b><br><br>" +
            #          "Median Nonmale Earnings: $%{y}<br>"+"<extra></extra>"),
                
            #   go.Bar(name='1-Year Male Median Earnings',
            #         x=other_grouped['cip_code'],
            #         y=other_grouped['earnings.highest.1_yr.male_median_earnings'].round(-3),
            #         opacity = opacity,
            #         hovertext = other_grouped['CIPTitle'],
            #         hovertemplate = "<b>%{hovertext}</b><br><br>" +
            #          "Median Male Earnings: $%{y}<br>"+"<extra></extra>")
        ]
    )
    grouped.update_layout(barmode='group', title='First Year Post-Grad Median Earnings (Male and Nonmale Graduates)',
                          xaxis_title='CIP Code',
                          yaxis_title='Reported Post-Grad Earnings',
                          template='ggplot2',
                          legend={'traceorder':'normal', 'borderwidth':1, 'yanchor':'middle', 'y':1.02, 'xanchor':'right', 'x':0.99})
    
    return grouped