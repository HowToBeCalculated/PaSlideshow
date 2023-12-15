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

HEIGHT = '650px'
IMAGE_DURATION = 10 * 1000 # in seconds
VIDEO_DURATION = 30 * 1000 # in seconds
LAST_IMAGE_LIMIT_PCT = .5

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
        dcc.Upload(
            id='upload-files',
            children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
            multiple=True,  # Allow multiple files
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            }
        ),
        html.Div(id='file-list'),
        dbc.Button('Submit', id='submit-button', n_clicks=0),
        html.Div(id='upload-status')
    ])
],
style={
    'background': 'linear-gradient(to right, #6dd5ed, #2193b0)',  # Example gradient
    'minHeight': '100vh',
    'minWidth': '100vw',
    'padding': '0',
    'margin': '0'
})

def parse_contents(contents, filename):
    # This function can be expanded based on file type
    # For now, we'll assume they are images for simplicity
    return html.Img(src=contents, style={'maxWidth': '100%', 'height': 'auto'})

@callback(
    Output('file-list', 'children'),
    [Input('upload-files', 'contents')],
    [State('upload-files', 'filename')]
)
def update_file_list(contents, filenames):
    if contents is None:
        return 'No file selected'
    if len(contents) == 1:
        # Display the file if only one is selected
        return parse_contents(contents[0], filenames[0])
    else:
        # Display a message if multiple files are selected
        return f'{len(contents)} items selected'

@callback(
    Output('upload-status', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('upload-files', 'contents'),
     State('upload-files', 'filename')]
)
def upload_to_s3(n_clicks, contents, filenames):
    if n_clicks > 0 and contents is not None:
        for content, filename in zip(contents, filenames):
            # Assuming the content is base64 encoded
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            s3_client.Object(bucket_name, datetime.utcnow().isoformat() + filename).put(Body=decoded)
        
        return 'Files uploaded successfully'
    return 'No files uploaded'
