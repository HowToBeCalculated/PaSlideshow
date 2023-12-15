import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
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
        return [create_presigned_url_download(bucket_name, image) for image in images]
    except NoCredentialsError:
        return []

def get_random_media_element(media_list, last_images):
    if not media_list:
        return html.Div("No images available or unable to load images.")
    
    while (url := random.choice(media_list)) in last_images:
        ...

    if len(last_images) >= int(len(media_list) * LAST_IMAGE_LIMIT_PCT):
        last_images.pop(0)

    last_images.append(url)
    # print(last_images)

    if '.mov?' in url or '.mp4?' in url:
        # For videos
        element = html.Video(src=url, autoPlay=True, controls=True, muted=True, style={"height": HEIGHT, "width": "auto"})
        duration = VIDEO_DURATION
    else:
        # For images
        element =  html.Img(src=url, style={"height": HEIGHT, "width": "auto"})
        duration = IMAGE_DURATION

    return element, duration, last_images

dash.register_page(__name__, path='/slideshow')

layout = html.Div([
    dbc.Container([
        dcc.Store(id='last-images', data=[]),
        html.Br(),
        html.Div(
            id='slideshow-container',
            style={
                'display': 'flex',
                'alignItems': 'center',  # Vertical centering
                'justifyContent': 'center',  # Horizontal centering
                'height': HEIGHT,  # Adjust as needed
                'margin': 'auto',
                'overflow': 'hidden'  # To handle media larger than the container
            }
        ),
        dcc.Interval(
            id='interval-component',
            interval=IMAGE_DURATION,
            n_intervals=0
        )
    ])
],
style={
    'background': 'linear-gradient(to right, #6dd5ed, #2193b0)',  # Example gradient
    'minHeight': '100vh',
    'minWidth': '100vw',
    'padding': '0',
    'margin': '0'
})

@callback(
    Output('slideshow-container', 'children'),
    Output('interval-component', 'interval'),
    Output('last-images', 'data'),
    Input('interval-component', 'n_intervals'),
    State('last-images', 'data'),
)
def update_image(_, last_images: list[str]):
    media_list = get_image_urls_from_s3()
    return get_random_media_element(media_list, last_images)
