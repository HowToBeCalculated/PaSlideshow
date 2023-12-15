import dash
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

dash.register_page(__name__, path='/')

# Define the layout of the app
layout = html.Div([dbc.Container([
    dbc.Row(
        dbc.Col(
            html.H1("In Loving Memory of Pa", className="text-center"),
            width=12
        )
    ),
    dbc.Row(
        dbc.Col(
            dbc.CardImg(src="assets/pa.jpeg", style={"height": "350px", "object-fit": "contain"}, top=True),
        )
    ),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Gallery", className="card-title"),
                    html.P("Explore the gallery", className="card-text"),
                    dbc.Button("Go to Gallery", href="/gallery", color="primary"),
                ])
            ]),
            md=4
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Slideshow", className="card-title"),
                    html.P("View our slideshow", className="card-text"),
                    dbc.Button("Go to Slideshow", href="/slideshow", color="primary"),
                ])
            ]),
            md=4
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Upload", className="card-title"),
                    html.P("Upload your images", className="card-text"),
                    dbc.Button("Go to Upload", href="/upload", color="primary"),
                ])
            ]),
            md=4
        )
    ], className="mb-4")
], fluid=True)
],
style={
    'background': 'linear-gradient(to right, #6dd5ed, #2193b0)',  # Example gradient
    'minHeight': '100vh',
    'minWidth': '100vw',
    'padding': '0',
    'margin': '0'
})