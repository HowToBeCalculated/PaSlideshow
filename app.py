import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import os

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# needed for gunicorn/wsgi to connect
server = app.server

app.layout = dash.page_container

if __name__ == '__main__':
    if os.getenv('DASH_ENV') == 'development':
        app.run(debug=True)
    else:
        app.config.suppress_callback_exceptions = True
        app.enable_dev_tools(debug=False)
        app.run_server(host='0.0.0.0', port=8050)
