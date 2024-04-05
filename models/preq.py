from app import app
from datetime import datetime
from bson import json_util
from flask_mongoengine import MongoEngine
from app.models import db
from app.config  import MONGO_ALIAS3

class Preq(db.Document):
    """Faq model for AllFieldsModel and pagination."""

    meta = {
        "db_alias":MONGO_ALIAS3,
        'collection': 'PREQ'
    }
    form_id = db.StringField(max_length=60)
    proposal_id = db.StringField(max_length=60)
    urls = db.ListField()
    client_type = db.StringField(max_length=60)
    region =db.StringField(max_length=100)
    recipient_email = db.StringField(max_length=60)
    contact_email = db.StringField(max_length=60)
    business_individual = db.StringField(max_length=20)
    full_name = db.StringField(max_length=60)
    contact_first_name = db.StringField(max_length=60)    
    total_url = db.IntField(default=1)
    date = db.DateField()
    
    methods = db.ListField()
    google_extension = db.ListField(blank=True, null=True, default=None)
    notes = db.StringField(max_length=60)
    application_type = db.StringField(max_length=60)
    retail_price = db.IntField(default=0)
    discount_request = db.BooleanField(default=False)
    payment_upon_completion = db.BooleanField(default=False)
    request_price = db.StringField(blank=True, null=True, default=None)
    discount_length = db.StringField(blank=True, null=True, default=None)
    discount_reason = db.StringField(blank=True, null=True, default=None)


    
    
