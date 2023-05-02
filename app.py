import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

# from forms import UserAddForm, LoginForm, MessageForm, CsrfForm, UserUpdateForm
# from models import db, connect_db, User, Message

load_dotenv()

CURR_USER_KEY = "curr_user"


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
# toolbar = DebugToolbarExtension(app)

# connect_db(app)


@app.post('/add-photo')
def add_photo():
    """ Add photo data to database and upload to AWS"""

    