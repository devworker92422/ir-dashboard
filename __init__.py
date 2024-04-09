# -*- coding: utf-8 -*-
# @Author: Dima Sumaroka
# @Date:   2017-01-23 13:08:19
# @Last Modified by:   Dima Sumaroka
# @Last Modified time: 2017-02-03 14:22:26

import os
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail, Message


from app.models import db

from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__, static_folder="public")

lm = LoginManager()
lm.login_view = ".login"
app.config.from_object(f"app.config.{os.getenv('FLASK_ENV')}Config")
app.secret_key = app.config["SECRET_KEY"]

db.init_app(app)
lm.init_app(app)
mail = Mail(app)

app.APP_URL = "http://127.0.0.1:5000"

from app import views
from app import api

app.add_url_rule("/", view_func=views.results, methods=["GET", "POST"])
app.add_url_rule("/complete", view_func=views.complete, methods=["GET", "POST"])
app.add_url_rule("/progress", view_func=views.progress, methods=["GET", "POST"])
app.add_url_rule("/detail", view_func=views.detail, methods=["GET", "POST"])
app.add_url_rule("/lead", view_func=views.lead, methods=["GET", "POST"])
app.add_url_rule("/login", view_func=views.login, methods=["GET", "POST"])
app.add_url_rule("/signup", view_func=views.signup, methods=["GET", "POST"])
app.add_url_rule("/logout", view_func=views.logout, methods=["GET", "POST"])
app.add_url_rule("/profile", view_func=views.profile, methods=["GET", "POST"])
app.add_url_rule("/contact", view_func=views.contact, methods=["GET", "POST"])
app.add_url_rule("/submit", view_func=views.submit, methods=["GET", "POST"])
app.add_url_rule("/faq", view_func=views.faq, methods=["GET", "POST", "DELETE"])
app.add_url_rule("/report", view_func=views.report, methods=["GET", "POST", "DELETE"])
app.add_url_rule("/staffs", view_func=views.staffs, methods=["GET", "POST", "DELETE"])
app.add_url_rule("/resetPassword", view_func=views.resetPassword, methods=["GET", "POST", "DELETE"])
app.add_url_rule("/checkResetPassword", view_func=views.checkResetPassword, methods=["GET", "POST", "DELETE"])


# APIs
app.add_url_rule("/api/urls", view_func=api.urls, methods=["GET", "POST"])
app.add_url_rule("/api/progressUrl", view_func=api.urls_in_progress, methods=["GET", "POST"])
app.add_url_rule("/api/completeUrl", view_func=api.urls_completed, methods=["GET", "POST"])
app.add_url_rule("/api/leads", view_func=api.leads, methods=["GET", "POST"])
app.add_url_rule("/api/export", view_func=api.export, methods=["GET", "POST"])
app.add_url_rule("/api/getClients",view_func=api.getClients,methods=["GET","POST"])
app.add_url_rule("/api/getStaffData",view_func=api.getStaffData,methods=["GET","POST"])
app.add_url_rule("/api/getAllStaffs",view_func=api.getAllStaffs,methods=["GET","POST"])
app.add_url_rule("/api/saveStaff",view_func=api.saveStaff,methods=["GET","POST"])
app.add_url_rule("/api/removeStaff",view_func=api.removeStaff,methods=["GET","POST"])
app.add_url_rule("/api/addNewStaff",view_func=api.addNewStaff,methods=["GET","POST"])
app.add_url_rule("/api/updateStatus",view_func=api.updateStatus,methods=["GET","POST"])
app.add_url_rule("/api/updateGoogleStatus",view_func=api.updateGoogleStatus,methods=["GET","POST"])
# app.add_url_rule("/api/htmlToPdf",view_func=api.htmlToPdf,methods=["GET","POST"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80,  debug=True)
