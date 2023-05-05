import os
import boto3
from dotenv import load_dotenv


from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS
from models import db, connect_db, Photo
import io
from io import BytesIO
import urllib.request
from urllib.request import urlopen
from filter_functions import b_and_w, posterize
from utils import create_large_image, create_small_image

# from forms import UserAddForm, LoginForm, MessageForm, CsrfForm, UserUpdateForm
# from models import db, connect_db, User, Message

load_dotenv()

CURR_USER_KEY = "curr_user"

BUCKET_NAME = os.environ['BUCKET_NAME']

REGION = os.environ['REGION']

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", 'postgresql:///pixly')
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

s3 = boto3.client(
    "s3",
    "us-east-1",
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
)
response = s3.list_buckets()

# Output the bucket names
print('Existing buckets:')
for bucket in response['Buckets']:
    print(f'  {bucket["Name"]}')


@app.post('/upload')
def add_photo():
    """ Add photo data to database and upload to AWS
    Returns json:
    {large_url:"http://....", small_url:"http://...", key:"bw-img.jpg", make:"Nikon",
     model:"D70", date:"12-03-22"
    """

    uploaded_photo = request.files["photo"]
    file_name = uploaded_photo.filename

    image = Image.open(uploaded_photo)


    large_img_data = create_large_image(image, file_name)
    small_img_data = create_small_image(image, file_name)

    metadata = image.getexif()

    data_with_tags = {}

    # iterating over all EXIF data fields
    for tag_id in metadata:
    # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = metadata.get(tag_id)
    # decode bytes
        if isinstance(data, bytes):
            data = data.decode()

        data_with_tags[tag] = data

    key = uploaded_photo.filename
    make = data_with_tags.get('Make')
    model = data_with_tags.get('Model')
    date = data_with_tags.get("DateTime")

    try:
        photo = Photo.add_image(large_url=large_img_data['url'], small_url=small_img_data["url"], key=key, make=make, model=model, date=date)
        db.session.commit()
        s3.upload_fileobj(large_img_data["file"], BUCKET_NAME, large_img_data["file_name"])
        s3.upload_fileobj(small_img_data["file"], BUCKET_NAME, small_img_data["file_name"])
        photo_serialized = photo.serialize()
        return (jsonify(photo=photo_serialized), 201)

    except IntegrityError:
        db.session.rollback()
        return (jsonify(error="Duplicate file name"), 400)


@app.get("/photos")
def get_pictures():
    """ Gets image data from database and returns json: 
    {large_url:"http://....", small_url:"http://...", key:"bw-img.jpg", make:"Nikon",
    model:"D70", date:"12-03-22"""

    photos = Photo.query.all()
    print("photos, ", photos)
    serialized = [p.serialize() for p in photos]

    return jsonify(photos=serialized)

@app.post("/edit")
def edit_photo():
    """ takes json data: {'key': 'image.jpg' 'method': 'bw'}.
    Applies filter method specified by method.
    Returns json {large_url:"http://....", small_url:"http://...", key:"bw-img.jpg",
    make:"Nikon",
    model:"D70", date:"12-03-22"}  """

    photo_key = request.json["key"]
    method = request.json["method"]

    img_to_edit = Image.open(urlopen(f"https://s3.us-west-1.amazonaws.com/kmdeakers-pix.ly/{photo_key}"))
    # img_to_edit = Image.open(urlopen(f'https://s3.amazonaws.com/evanhesketh-pix.ly/{photo_key}'))

    metadata = img_to_edit.getexif()

    data_with_tags = {}
    # iterating over all EXIF data fields
    for tag_id in metadata:
    # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = metadata.get(tag_id)
    # decode bytes
        if isinstance(data, bytes):
            data = data.decode()

        data_with_tags[tag] = data
        # print(f"{tag:25}: {data}")

    edited_file_data = ""

    if method == 'bw':
        edited_file_data = b_and_w(photo_key, img_to_edit)
    if method == 'posterize':
        edited_file_data = posterize(photo_key, img_to_edit)

    large_url = edited_file_data['large_url']
    small_url = edited_file_data['small_url']
    key = edited_file_data['large_file_name']
    make = data_with_tags.get('Make')
    model = data_with_tags.get('Model')
    date = data_with_tags.get("DateTime")

    try:
        photo = Photo.add_image(large_url=large_url, small_url=small_url, key=key, make=make, model=model, date=date)
        db.session.commit()
        s3.upload_fileobj(edited_file_data["small_file"], BUCKET_NAME, edited_file_data['small_file_name'])
        s3.upload_fileobj(edited_file_data["large_file"], BUCKET_NAME, edited_file_data['large_file_name'])
        photo_serialized = photo.serialize()
        return (jsonify(photo=photo_serialized), 201)

    except IntegrityError:
        db.session.rollback()
        return (jsonify(error="Duplicate file name"), 400)


