
from app.models import db
from app.config import MONGO_ALIAS1, MONGO_ALIAS2
from datetime import datetime
class DmcaApp(db.Document):
    """DmcaApp model for AllFieldsModel and pagination."""

    meta = {        
        'db_alias': MONGO_ALIAS1,
        'collection': 'dmcaapp'
    }
    requester_email = db.StringField(max_length=100)
    client_email = db.StringField(max_length=100)
    client_name = db.StringField(max_length=100, default="")
    url_data = db.StringField()
    date = db.StringField(default="")
    urlstatus = db.ListField(required=False)
    submission_count = db.IntField(default=1)
    latest_update=db.DateTimeField(default=datetime.now)