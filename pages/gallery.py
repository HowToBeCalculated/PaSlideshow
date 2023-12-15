import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import boto3
from botocore.exceptions import NoCredentialsError
import json
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
bucket_name = os.getenv('AWS_BUCKET_NAME')  # replace with your bucket name

def create_presigned_url_download(bucket_name, object_name, expiration=600):
    try:
        response = s3_client.meta.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name,
                    'Key': object_name},
            ExpiresIn=expiration
        )
    except NoCredentialsError:
        return None
    return response

def get_image_urls_from_s3():
    try:
        response = s3_client.meta.client.list_objects(Bucket=bucket_name)
        images = [content['Key'] for content in response.get('Contents', []) if content['Key'].lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.mov', '.mp4'))]
        images = [create_presigned_url_download(bucket_name, image) for image in images]
        random.shuffle(images)
        return images
    except NoCredentialsError:
        return []

def create_media_card(url):
    is_video = '.mov?' in url or '.mp4?' in url
    thumbnail = url  # Assuming direct link to the image or a thumbnail

    dynamic_id = {
        "type": "dynamic-media",
        "index": url
    }
    card_content = [
        dmc.Image(src=thumbnail, fit="cover", height=200, radius="md"),
        dmc.Button(
            "View",
            variant="light",
            color="blue",
            fullWidth=True,
            mt="md",
            radius="md",
            id=dynamic_id,
            n_clicks=0
        )
    ]

    card = dmc.Card(
        card_content,
        style={"width": "18rem"},
        className="m-2",
        shadow="sm",
        radius="md",
    )

    return card

def create_gallery_layout():
    media_urls = get_image_urls_from_s3()
    cards = [create_media_card(url) for url in media_urls]
    return dmc.SimpleGrid(
        cols=4,  # Set the number of columns
        spacing="lg",
        breakpoints=[
            {"maxWidth": "xs", "cols": 1, "spacing": "sm"},
            {"maxWidth": "sm", "cols": 2, "spacing": "md"},
            {"maxWidth": "lg", "cols": 3, "spacing": "lg"}
        ],
        children=cards
    )

dash.register_page(__name__, path='/gallery')


layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dbc.Modal([
        dbc.ModalBody(html.Div(id='modal-body')),
    ], id='modal', size="lg")
],
style={
    'background': 'linear-gradient(to right, #6dd5ed, #2193b0)',  # Example gradient
    'minHeight': '100vh',
    'minWidth': '100vw',
    'padding': '0',
    'margin': '0'
}
)

@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/gallery':
        return create_gallery_layout()
    else:
        return "Welcome to the Dashboard"

@callback(
    Output('modal', 'is_open'),
    Output('modal-body', 'children'),
    [Input({'type': 'dynamic-media', 'index': dash.ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def display_media(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, None

    # Extract button ID and URL from the triggered context
    button_id = ctx.triggered[0]['prop_id'].split('}.')[0] + '}'
    button_data = json.loads(button_id)
    media_url = button_data['index']

    if '.mov?' in media_url or '.mp4?' in media_url:
        content = html.Video(src=media_url, controls=True, style={"width": "100%"})
    else:
        content = html.Img(src=media_url, style={"width": "100%"})

    return True, content
