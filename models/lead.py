from flask_login import login_user, logout_user, login_required, UserMixin

from werkzeug.security import check_password_hash, generate_password_hash
# from passlib.apps import custom_app_context as pwd_context
from app import app
from datetime import datetime
from bson import json_util
from flask_mongoengine import MongoEngine
from app.models import db
from app.config import MONGO_ALIAS1, MONGO_ALIAS2

class Lead(db.Document):
    """lead model for AllFieldsModel and pagination."""

    meta = {        
        'db_alias': MONGO_ALIAS2,
        'collection': 'leads'
    }
    name = db.StringField(max_length=100, default="")
    email = db.StringField(max_length=100, default="")
    address = db.StringField(max_length=100, default="")
    review_score = db.FloatField()
    total_reviews = db.IntField()
    phone = db.StringField(default="")
    reviews = db.ListField(db.StringField(default=""))
