import os
import boto3
from dotenv import load_dotenv


from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from PIL import Image
from PIL.ExifTags import TAGS
from models import db, connect_db, Photo
from urllib.request import urlopen

from filter_functions import b_and_w, posterize
from utils import create_standardized_image

load_dotenv()

CURR_USER_KEY = "curr_user"

BUCKET_NAME = os.environ['BUCKET_NAME']

REGION = os.environ['REGION']

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///pixly')
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
    {large_url:"http://....", file_name:"bw-img.jpg", make:"Nikon",
     model:"D70", date:"12-03-22"
    """

    uploaded_photo = request.files["photo"]
    file_name = uploaded_photo.filename

    image = Image.open(uploaded_photo)

    img_data = create_standardized_image(image, file_name)

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

    make = data_with_tags.get('Make')
    model = data_with_tags.get('Model')
    date = data_with_tags.get("DateTime")

    try:
        photo = Photo.add_image(url=img_data['url'],
                                file_name=img_data['file_name'], make=make, model=model, date=date)
        db.session.commit()

        s3.upload_fileobj(img_data["image"],
                          BUCKET_NAME, img_data["file_name"])
        photo_serialized = photo.serialize()

        return (jsonify(photo=photo_serialized), 201)

    except IntegrityError as e:
        print("Error: ", e)

        db.session.rollback()
        return (jsonify(error="Duplicate file name"), 400)


@app.get("/photos")
def get_pictures():
    """ Gets image data from database and returns json:
    {url:"http://....", file_name:"bw-img.jpg", make:"Nikon",
    model:"D70", date:"12-03-22"""

    photos = Photo.query.all()
    serialized = [p.serialize() for p in photos]

    return jsonify(photos=serialized)


@app.post("/edit")
def edit_photo():
    """ takes json data: {'fileName': 'image.jpg' 'method': 'bw'}.
    Applies filter method specified by method.
    Returns json {url:"http://....", file_name:"bw-img.jpg",
    make:"Nikon",
    model:"D70", date:"12-03-22"}"""

    file_name = request.json["fileName"]
    method = request.json["method"]

    img_to_edit = Image.open(
        urlopen(f"https://s3.amazonaws.com/evanhesketh-pix.ly/{file_name}"))

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
        edited_file_data = b_and_w(file_name, img_to_edit)
    if method == 'posterize':
        edited_file_data = posterize(file_name, img_to_edit)

    url = edited_file_data['url']
    file_name = edited_file_data['file_name']
    make = data_with_tags.get('Make')
    model = data_with_tags.get('Model')
    date = data_with_tags.get("DateTime")

    try:
        photo = Photo.add_image(
            url=url, file_name=file_name, make=make, model=model, date=date)
        db.session.commit()

        s3.upload_fileobj(
            edited_file_data["image"], BUCKET_NAME, edited_file_data['file_name'])
        photo_serialized = photo.serialize()

        return (jsonify(photo=photo_serialized), 201)

    except IntegrityError as e:
        print("Error: ", e)

        db.session.rollback()
        return (jsonify(error="Duplicate file name"), 400)
