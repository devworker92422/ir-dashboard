from flask_login import login_user, logout_user, login_required, UserMixin

from werkzeug.security import check_password_hash, generate_password_hash
# from passlib.apps import custom_app_context as pwd_context
from app import app
from datetime import datetime
from bson import json_util
from flask_mongoengine import MongoEngine
from app.models import db
from app.config import MONGO_ALIAS1, MONGO_ALIAS2

class Contact(db.Document):
    """Contact model for AllFieldsModel and pagination."""

    meta = {        
        'db_alias': MONGO_ALIAS2,
        'collection': 'contacts'
    }
    requester_email = db.StringField(max_length=100)
    client_email = db.StringField(max_length=100)
    client_name = db.StringField(max_length=100, default="")
    url = db.URLField()
    status = db.IntField()
    date = db.StringField(default="")
    date_checked = db.StringField(default="")
    time_checked = db.StringField(default="")
    google_status = db.StringField(default="")
