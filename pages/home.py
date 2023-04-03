import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import os

dash.register_page(__name__, path='/', title="ExploreU")

topics = ['Biology', 'Chemistry', 'Physics', 'Mathematics', 'Computer Science', 'Engineering', 'Psychology', 'Sociology', 'Anthropology', 'Political Science',
        'History', 'Philosophy', 'English', 'Education', 'Art', 'Music', 'Theater', 'Dance', 'Journalism', 'Business', 'Marketing', 'Economics', 'Finance',
        'Accounting', 'Management', 'International Business', 'Entrepreneurship', 'Human Resources', 'Law', 'Criminal Justice', 'Forensic Science',
        'Environmental Science', 'Geology', 'Geography', 'Agriculture', 'Nutrition', 'Public Health', 'Nursing', 'Medicine', 'Veterinary Science',
        'Dentistry', 'Physical Therapy', 'Occupational Therapy', 'Speech Therapy', 'Social Work', 'Counseling', 'Library Science', 'Archival Studies',
        'Information Technology', 'Data Science', 'Artificial Intelligence', 'Machine Learning', 'Cybersecurity', 'Cryptography', 'Web Development',
        'Mobile Development', 'Game Development', 'Multimedia', 'Graphic Design', 'Interior Design', 'Fashion Design', 'Industrial Design', 'Urban Planning',
        'Architecture', 'Real Estate', 'Aerospace Engineering', 'Mechanical Engineering', 'Electrical Engineering',
        'Civil Engineering', 'Chemical Engineering', 'Materials Science', 'Nuclear Engineering', 'Marine Science', 'Oceanography', 'Meteorology', 'Astronomy',
        'Zoology', 'Botany', 'Ecology', 'Conservation', 'Forestry', 'Horticulture', 'Sports Science', 'Kinesiology', 'Exercise Science',
        'Sports Medicine', 'Coaching', 'Physical Education', 'Recreation', 'Tourism', 'Hospitality', 'Culinary Arts', 'Wine Studies', 'Performing Arts',
        'Creative Writing', 'Agricultural Science', 'Astrophysics', 'Behavioral Science', 'Biochemistry', 'Biomedical Engineering', 'Biostatistics', 'Cognitive Science',
        'Communication Disorders', 'Comparative Literature', 'Criminology', 'Cultural Studies', 'Data Analytics',
        'Developmental Psychology', 'Early Childhood Education', 'East Asian Studies', 'Econometrics', 'Educational Psychology',
        'Electronics Engineering', 'Engineering Physics', 'Entomology', 'Environmental Engineering', 'Ethnic Studies', 'European Studies',
        'Evolutionary Biology', 'Film Studies', 'Food Science', 'Literature','Linguistics', 'Gender Studies', 'Genetics',
        'Global Studies', 'Health Administration', 'Healthcare Management', 'Hispanic Studies',
        'Industrial Psychology', 'Information Science', 'International Studies', 'Jewish Studies', 'Latin American Studies',
        'Linguistic Anthropology', 'Marine Biology', 'Marketing', 'Materials Engineering', 'Medical Anthropology',
        'Medical Sociology', 'Medieval Studies', 'Microbiology', 'Middle Eastern Studies', 'Molecular Biology', 'Museum Management', 'Music Education', 'Neuroscience',
        'Nuclear Physics', 'Nursing', 'Organic Chemistry', 'Organizational Psychology', 'Paleontology', 'Peace and Conflict Studies',
        'Pediatric Nursing', 'Philosophy of Science', 'Physical Chemistry', 'Plant Science', 'Polymer Science',
        'Psychobiology', 'Public Administration', 'Public Policy', 'Quantum Physics', 'Radiation Oncology', 'Religious Studies',
        'Robotics', 'Science Education', 'Science Journalism', 'Science Writing',
        'Social Psychology', 'Social Statistics', 'Social Theory', 'Sociolinguistics', 'Software Engineering', 'Special Education',
        'Sport Management', 'Statistics', 'Structural Engineering', 'Supply Chain Management', 'Systems Biology', 'Theoretical Physics', 'Sports', 'Social media',
        'Video games', 'Fashion', 'TV shows', 'Movies', 'Politics', 'Climate change', 'Science fiction', 'Food', 'Travel', 'Fitness', 'Health',
        'Literature', 'Poetry', 'Photography', 'Beauty', 'Computer science', 'Coding', 'Space exploration', 'Nature', 'Animals',
        'Technology', 'Investing', 'Banking', 'Ethics', 'Human rights', 'Social justice', 'Teaching', 'Learning', 'Language learning', 'Writing', 'Blogging',
        'Public speaking', 'Debate', 'Drama', 'Improv', 'Stand-up comedy', 'Acting', 'Gymnastics', 'Skateboarding', 'Surfing', 'Snowboarding', 'Skiing', 'Swimming',
        'Gardening', 'Cooking', 'Baking', 'Non-Profit Organizations', 'Environmentalism', 'Religion', 'Spirituality',
        'Dieting', 'Weightlifting','Street art', 'Graffiti', 'Social activism', 'Mental health',
        'Virtual reality', 'Augmented reality', 'Social media marketing', 'Music production', 'Sound engineering', 'Sound design', 'Music theory',
        'Art history', 'Art restoration', 'Ceramics', 'Sculpture', 'Printmaking', 'Calligraphy', 'Digital art',
        'User interface design', 'Web design', 'Mobile app development', 'Blockchain technology',
        'Feminism', 'LGBTQ+ rights', 'Racial justice','Immigration Policy', 'Climate activism', 'Renewable energy', 'Sustainable agriculture', 'Urban planning', 'Archaeology',
        'Environmental science', 'Food science', 'Event planning']

search = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(dcc.Dropdown(topics, value=[], persistence=True, placeholder="Topic #1", id="topics-1")),
                        dbc.Col(dcc.Dropdown(topics, value=[], persistence=True, placeholder="Topic #2", id="topics-2")),
                        dbc.Col(dcc.Dropdown(topics, value=[], persistence=True, placeholder="Topic #3", id="topics-3")),
                        dbc.Col(dcc.Dropdown(topics, value=[], persistence=True, placeholder="Topic #4", id="topics-4")),
                        dbc.Col(dcc.Dropdown(topics, value=[], persistence=True, placeholder="Topic #5", id="topics-5"))
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
        dbc.Spinner(html.Div(id="cip-results"))
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
    [
        State('topics-1', 'value'),
        State('topics-2', 'value'),
        State('topics-3', 'value'),
        State('topics-4', 'value'),
        State('topics-5', 'value')
    ]
)
def update_results(click, topic1, topic2, topic3, topic4, topic5):
    # retrieve results from model here
    cip_results = ["45.06", "30.70", "11.01", "13.06"]
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