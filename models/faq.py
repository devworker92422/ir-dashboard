 
from flask_login import login_user, logout_user, login_required, UserMixin

from werkzeug.security import check_password_hash, generate_password_hash
# from passlib.apps import custom_app_context as pwd_context
from app import app
from datetime import datetime
from bson import json_util
from flask_mongoengine import MongoEngine
from app.models import db
from app.config  import MONGO_ALIAS1

class Faq(db.Document):
    """Faq model for AllFieldsModel and pagination."""

    meta = {
        "db_alias":MONGO_ALIAS1,
        'collection': 'faqs'
    }
    requester_email = db.StringField(max_length=60)
    client_email = db.StringField(max_length=60)
    question = db.StringField()
    answer = db.StringField()
    date = db.StringField(default="")
