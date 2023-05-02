import os
import boto3
from dotenv import load_dotenv


from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized
from utils import show_image
from werkzeug.utils import secure_filename

# from forms import UserAddForm, LoginForm, MessageForm, CsrfForm, UserUpdateForm
# from models import db, connect_db, User, Message

load_dotenv()

CURR_USER_KEY = "curr_user"

BUCKET_NAME = os.environ['BUCKET_NAME']

REGION = os.environ['REGION']

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
# app.config['AWS_ACCESS_KEY_ID'] = os.environ['AWS_ACCESS_KEY_ID']
# app.config['AWS_SECRET_ACCESS_KEY'] = os.environ['AWS_SECRET_ACCESS_KEY']
# toolbar = DebugToolbarExtension(app)

# connect_db(app)

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


@app.post('/add-photo')
def add_photo():
    """ Add photo data to database and upload to AWS"""

    uploaded_photo = request.files["photo"]
    print(uploaded_photo, " uploaded photo")

    file_name = secure_filename(uploaded_photo.filename)

    s3.upload_fileobj(uploaded_photo, BUCKET_NAME, file_name)

    return jsonify(key="Succes")

# @app.get('/photos')
# def get_photos():
#     """ Gets all photos from AWS server """

#     photo = s3.download_file(BUCKET_NAME, 'photo1', <FileStorage: 'takeoff.jpeg' ('image/jpeg')>)
#     print("photo ", photo)
#     return render_template('photos.html', photo=photo)

@app.get("/pics")
def list():
    contents = show_image(BUCKET_NAME)
    return render_template('photos.html', contents=contents)