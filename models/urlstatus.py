 

from flask_login import login_user, logout_user, login_required, UserMixin

from werkzeug.security import check_password_hash, generate_password_hash
# from passlib.apps import custom_app_context as pwd_context
from app import app
from datetime import datetime
from bson import json_util
from flask_mongoengine import MongoEngine
from app.models import db
from app.config import MONGO_ALIAS1, MONGO_ALIAS2

class Urlstatus(db.Document):
    """Urlstatus model for AllFieldsModel and pagination."""

    meta = {        
        'db_alias': MONGO_ALIAS1,
        'collection': 'urlstatus'
    }
    _id = db.ObjectIdField()
    requester_email = db.StringField(max_length=100)
    client_email = db.StringField(max_length=100)
    client_name = db.StringField(max_length=100, default="")
    url = db.URLField()
    status = db.StringField(default="")
    date = db.StringField(default="")
    date_checked = db.StringField(default="")
    time_checked = db.StringField(default="")
    google_status = db.StringField(default="")
    submission_count = db.IntField(default=1)
    latest_update=db.DateTimeField(default=datetime.now)
