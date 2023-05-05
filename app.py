import os
import boto3
from dotenv import load_dotenv


from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized
from utils import show_image
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS
from models import db, connect_db, Photo
import io
from io import BytesIO
import urllib.request
from urllib.request import urlopen
from filter_functions import b_and_w

# from forms import UserAddForm, LoginForm, MessageForm, CsrfForm, UserUpdateForm
# from models import db, connect_db, User, Message

load_dotenv()

CURR_USER_KEY = "curr_user"

BUCKET_NAME = os.environ['BUCKET_NAME']

REGION = os.environ['REGION']

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", 'postgresql:///pixly')
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
# app.config['AWS_ACCESS_KEY_ID'] = os.environ['AWS_ACCESS_KEY_ID']
# app.config['AWS_SECRET_ACCESS_KEY'] = os.environ['AWS_SECRET_ACCESS_KEY']
# toolbar = DebugToolbarExtension(app)

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
    """ Add photo data to database and upload to AWS"""
    print ("request.files", request.files)

    uploaded_photo = request.files["photo"]

    image = Image.open(uploaded_photo)
    print("image.formt: ", image.format)



    metadata = image.getexif()
    resized_image = ImageOps.contain(image, (600, 1000))
    print("resized_image.format", resized_image.format)
    # print("uploaded_photo.filename", uploaded_photo.filename)
    # print("resized_image.filename", resized_image.filename)

    in_mem_file = io.BytesIO()
    resized_image.save(in_mem_file, format="JPEG")
    in_mem_file.seek(0)

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

    print("data_with_tags ", data_with_tags)

    print("metadata ", metadata)


    resized_image.seek(0)
    file_name = uploaded_photo.filename

    url= f"https://s3.us-west-1.amazonaws.com/kmdeakers-pix.ly/{file_name}"
    # url= f"https://s3.amazonaws.com/evanhesketh-pix.ly/{file_name}"
    key = file_name
    make = data_with_tags.get('Make')
    model = data_with_tags.get('Model')
    date = data_with_tags.get("DateTime")

    try:
        photo = Photo.add_image(url=url, key=key, make=make, model=model, date=date)
        db.session.commit()
        s3.upload_fileobj(in_mem_file, BUCKET_NAME, file_name)
        photo_serialized = photo.serialize()
        return (jsonify(photo=photo_serialized), 201)

    except IntegrityError:
        db.session.rollback()
        return (jsonify(error="Duplicate file name"), 400)


@app.get("/photos")
def get_pictures():
    photos = Photo.query.all()
    print("photos, ", photos)
    serialized = [p.serialize() for p in photos]

    return jsonify(photos=serialized)

@app.post("/edit")
def edit_photo():
    photo_key = request.json["key"]

    file_name = photo_key.split('.')

    # bw_file_name = f'{file_name[0]}-bw.{file_name[1]}'

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

    # bw_image = ImageOps.grayscale(image=img_to_edit)

    # in_mem_file = io.BytesIO()
    # bw_image.save(in_mem_file, format="JPEG")
    # in_mem_file.seek(0)

    edited_file_data = b_and_w(file_name, img_to_edit)

    print("edidted_file_data[file]:", edited_file_data["file"])

    # url= f"https://s3.us-west-1.amazonaws.com/kmdeakers-pix.ly/{bw_file_name}"
    # url= f"https://s3.amazonaws.com/evanhesketh-pix.ly/{bw_file_name}"
    url = edited_file_data['url']
    key = edited_file_data['edited_file_name']
    make = data_with_tags.get('Make')
    model = data_with_tags.get('Model')
    date = data_with_tags.get("DateTime")

    try:
        photo = Photo.add_image(url=url, key=key, make=make, model=model, date=date)
        db.session.commit()
        s3.upload_fileobj(edited_file_data["file"], BUCKET_NAME, edited_file_data['edited_file_name'])
        photo_serialized = photo.serialize()
        return (jsonify(photo=photo_serialized), 201)

    except IntegrityError:
        db.session.rollback()
        return (jsonify(error="Duplicate file name"), 400)


