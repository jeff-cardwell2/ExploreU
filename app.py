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

app.layout = html.Div([dash.page_container])

if __name__ == '__main__':
    app.run_server(debug=True)