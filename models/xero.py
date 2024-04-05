from app import app
from datetime import datetime
from bson import json_util
from flask_mongoengine import MongoEngine
from app.models import db
from app.config  import MONGO_ALIAS3

class Xero(db.Document):
    """Faq model for AllFieldsModel and pagination."""

    meta = {
        "db_alias":MONGO_ALIAS3,
        'collection': 'XERO'
    }
    currency_code = db.StringField(max_length=60)
    date = db.DateField(max_length=60)
    due_date = db.DateField(max_length=60)
    amount_due = db.FloatField(default=0)
    amount_paid =db.FloatField(default=0)
    invoice_id = db.StringField(max_length=60)
    contact_email = db.StringField(max_length=60)
    refrence = db.StringField(max_length=100)
    contact_name = db.StringField(max_length=60)
    

    
    
