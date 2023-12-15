import base64
import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError
import os
import random

from dotenv import load_dotenv
load_dotenv() 

# Boto3 S3 setup
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
)
s3_client = session.resource('s3')
bucket_name = os.getenv('AWS_BUCKET_NAME')

dash.register_page(__name__, path='/upload')

layout = html.Div([
    dbc.Container([
        dmc.Paper(
            dcc.Upload(
                id='upload-files',
                children=html.Div([
                    dmc.Center(dmc.Text("Drag and Drop or ", size='md')),
                    dmc.Center(html.A('Select Files', style={'fontWeight': 'bold', 'color': '#007bff'}))
                ], style={'padding': '20px'}),
                multiple=True,  # Allow multiple files
                style={
                    'width': '100%',
                    'height': '150px',
                    'lineHeight': '60px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px',
                    'padding': '20px'
                }
            ),
            withBorder=True,
            shadow='sm',
            radius='md',
            p='md'
        ),
        dmc.Space(h='md'),
        dmc.Center(dbc.Button('Submit', id='submit-button', n_clicks=0, color='primary')),
        dmc.Space(h='lg'),
        html.Div(id='file-list'),
        html.Div(id='upload-status')
    ], fluid=True)
],
style={
    'background': 'linear-gradient(to right, #6dd5ed, #2193b0)',
    'minHeight': '100vh',
    'padding': '20px'
})

def parse_contents(contents, filename):
    return html.Img(src=contents, style={'maxWidth': '100%', 'height': 'auto'})

@callback(
    Output('file-list', 'children'),
    [Input('upload-files', 'contents')],
    [State('upload-files', 'filename')]
)
def update_file_list(contents, filenames):
    if contents is None:
        return dmc.Alert('No file selected', color='red')
    if len(contents) == 1:
        return parse_contents(contents[0], filenames[0])
    else:
        return dmc.Alert(f'{len(contents)} items selected', color='blue')

@callback(
    Output('upload-status', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('upload-files', 'contents'),
     State('upload-files', 'filename')]
)
def upload_to_s3(n_clicks, contents, filenames):
    if n_clicks > 0 and contents is not None:
        for content, filename in zip(contents, filenames):
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            s3_client.Object(bucket_name, datetime.utcnow().isoformat() + filename).put(Body=decoded)
        
        return dmc.Alert('Files uploaded successfully!', color='green')
    return dmc.Alert('No files uploaded', color='red')
