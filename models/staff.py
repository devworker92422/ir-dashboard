from app import app
from datetime import datetime
from bson import json_util
from flask_mongoengine import MongoEngine
from app.models import db
from app.config  import MONGO_ALIAS1

class Staff(db.Document):
    """Faq model for AllFieldsModel and pagination."""

    meta = {
        "db_alias":MONGO_ALIAS1,
        'collection': 'STAFF'
    }
    email = db.StringField(max_length=60,default="")
    name = db.StringField(max_length=60,default="")
    role = db.IntField(default=0)
    region =db.StringField(max_length=100,default="")
    

    
    
