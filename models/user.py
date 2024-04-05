# -*- coding: utf-8 -*-
# @Author: Dima Sumaroka
# @Date:   2017-01-23 13:06:16
# @Last Modified by:   Dima Sumaroka
# @Last Modified time: 2017-02-08 14:16:00

from flask_login import login_user, logout_user, login_required, UserMixin

from werkzeug.security import check_password_hash, generate_password_hash
# from passlib.apps import custom_app_context as pwd_context
from datetime import datetime
from bson import json_util

from app import app
from app.models import db
from app.config import MONGO_ALIAS1, MONGO_ALIAS2


class User(UserMixin, db.Document):
    username = db.StringField(max_length=30)
    email = db.StringField()
    password_hash = db.StringField()
    phone = db.StringField()
    createdAt = db.DateTimeField(default=datetime.now)
    updatedAt = db.DateTimeField(default=datetime.now)
    role = db.IntField(default=0)
    region=db.StringField(default="")
    staff_name = db.StringField(default="",max_length=60)
    resetHash = db.StringField(required=False)
    password_new = db.StringField(required=False)
    meta = {
        "db_alias":MONGO_ALIAS1,
        'collection': 'users'
    }

 
    def is_authenticated(self):
        return True
    def is_admin(self):
        return self.email == "team@internetremovals.com"


    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password, "sha256")

    def set_email(self, email):
        self.email = email

    def set_phone(self, phone):
        self.phone = phone

    def set_username(self, username):
        self.username = username

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)