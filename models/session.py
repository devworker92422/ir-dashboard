 

from flask_login import login_user, logout_user, login_required, UserMixin

from werkzeug.security import check_password_hash, generate_password_hash
# from passlib.apps import custom_app_context as pwd_context
from app import app
from datetime import datetime
from bson import json_util
from flask_mongoengine import MongoEngine
from app.models import db
from app.config import MONGO_ALIAS1

class Session(db.Document):
    """Session model for AllFieldsModel and pagination."""

    meta = {
        "db_alias":MONGO_ALIAS1,
        'collection': 'sessions'
    }
    user_id = db.ObjectIdField(required=True)
    # email = db.StringField(max_length=60)
    session_id = db.StringField()
    success = db.BooleanField()