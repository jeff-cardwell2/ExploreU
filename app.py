import dash
from dash import DiskcacheManager, Dash, dcc, html, dash_table as dt
import dash_bootstrap_components as dbc

import diskcache
cache = diskcache.Cache("./cache")
bcm = DiskcacheManager(cache)

THEME = dbc.themes.LUMEN

app = Dash(
    __name__,
    external_stylesheets=[THEME, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css"],
    use_pages=True, 
    background_callback_manager=bcm
)
server = app.server
app.title = 'ExploreU'

header = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(src=app.get_asset_url('icon.png'), height="25px")
                        ),
                        dbc.Col(
                            dbc.NavbarBrand("ExploreU", class_name="ms-2"),
                        )
                    ],
                    align="center",
                    class_name="g-0",
                ),
                href=dash.page_registry['pages.home']['path'],
                style={"textDecoration": "none", 'fontWeight':'bold'},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.A('Code', href="https://github.com/jeff-cardwell2/SI699-Project", target="_blank"),
                        width="auto",
                        className="nav-link"
                    )
                ],
                className="g-0",
            )
        ],
        class_name="mx-1",
        fluid=True
    ),
    color="dark",
    dark=True,
)

app.layout = html.Div([header, dash.page_container])

if __name__ == '__main__':
    app.run_server(debug=True)