# -*- coding: utf-8 -*-
# @Author: Tahiana
# @Date:   2023-03-23 13:08:19
# @Last Modified by:   Tahiana
# @Last Modified time: 2023-03-28 14:15:54

from flask import Flask, flash, render_template, request, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from bson import json_util, ObjectId
from flask_mail import Mail, Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib, ssl
from urllib.parse import urlparse, urlunparse
from werkzeug.security import generate_password_hash
from datetime import datetime
import json
import base64
import pandas as pd

from mongoengine.errors import ValidationError
from mongoengine.queryset.visitor import Q

from app import mail
from app.models.user import User
from app.models.urlstatus import Urlstatus
from app.models.faq import Faq
from app.models.session import Session
from app import app, lm
from app.models.preq import Preq
from app.models.dmcaapp import DmcaApp
import requests
import io
import math
from urllib.parse import urlparse
import sys
try:
    sys.setdefaultencoding('utf-8')
except:
    pass
import secrets
from WHITELIST import get_successlist

def login():
    if request.method == "GET":
        return render_template("login.html",role=0)

    response = {"success": False, "response": " "}
    email = request.form.get("email")
    password = request.form.get("password")
    if email and password:
        user = User.objects(email=email).first()
        if user and User.validate_login(user.password_hash, password):
            user_obj = user
            if login_user(user_obj):
                sess = Session(user_id=user.id, session_id=session["_id"], success=True)
                sess.save()
                return redirect("/")
        else:
            response["response"] = "Worng password"
            flash("Wrong Password", "danger")
            return redirect(url_for("login"))
    else:
        response["response"] = "Username or password not entered"
        flash("Username or password not entered", "danger")
        return redirect(url_for("login"))
    
def resetPassword():
    if request.method == "GET":
        return render_template("resetPassword.html",role=0)
    role = 0
    email = request.form.get("email")
    pwd_new = request.form.get("pwd_new")
    pwd_check = request.form.get("pwd_check")
    if(pwd_new != pwd_check):
        flash("Password is not matching. Please try again.","warning")
        return render_template("resetPassword.html",role=role)
    
    token = secrets.token_urlsafe(16)

    user = User.objects(email=email).first()

    if user is None:
        flash("Email not found. Please try again.","warning")
        return render_template("resetPassword.html",role=role)
    client_name = user.username
    
    verify_url = f"https://ir-dashboard.com/checkResetPassword?token={token}&email={email}"

    User.objects(email=email).update_one(set__password_new=pwd_new, set__resetHash=token)

    message = MIMEMultipart()
    message["Subject"] = f"Password Reset Request - {client_name}"
    message["From"] = "Internet Removals DMCA Team"
    message["To"] = email
    body = f"""<html><body><p>Dear Sir or Madam,</p>
<p>We've received request for resetting password of your account, To confirm your new password, please follow the link below.</p>
<p><a href="{verify_url}">{verify_url}</a></p>
<p>Kind Regards,<br>
Internet Removals<br>
team@internetremovals.com<br>
<a href="https://internetremovals.com/">https://internetremovals.com/</a>
<p>"Managing DMCA notices and compliance is difficult. If you want help with this, enquire about our DMCA Agent Services. We process DMCA notices on your behalf and ensure compliance."</p>
</body></html>"""

    message.attach(MIMEText(body, "html"))

    # Send email
    context = ssl.create_default_context()
    smtp_server = "smtp.gmail.com"
    from_address = "internetremovalsdmcaagent3@gmail.com"
    password = "pnuafzhqygffupxg"

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, 587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(from_address, password)

        try:
            server.sendmail("team@internetremovals.com", str(email), message.as_string())
            # successes.extend(urls)
        except smtplib.SMTPException as e:
            # failures.extend(urls)
            print(f"An error occurred while sending email: {e}")

    flash("Password Reset confirmation email has been sent to your email. Please check.","success")
    flash(verify_url,"success")
    return render_template("resetPassword.html",role=role)

def checkResetPassword():
    token =request.args.get("token")
    email = request.args.get("email")
    user = User.objects(email=email).first()
    if(token == user.resetHash):
        new_password = user.password_new
        user.hash_password(password=new_password)
        User.objects(email=email).update_one(set__password_hash=generate_password_hash(new_password,"sha256"))
        flash("Password reset successful.", "success")
        return render_template("checkResetPassword.html",role=0)
    else:
        flash("This link is expired.", "danger")
        return render_template("checkResetPassword.html",role=0)

def signup():
    if request.method == "GET":
        return render_template("signup.html",role=0)
    role=0

    response = {"success": False, "response": " "}
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")

    if username is None or password is None:
        flash("user name or password is not provided.", "danger")
        return render_template("signup.html",role=role)

    if User.objects(username=username).first() is not None:
        flash("Username is already taken", "danger")
        return render_template("signup.html",role=role)

    if User.objects(email=email).first() is not None:
        flash("Email is already taken.", "danger")
        return render_template("signup.html",role=role)

    if Urlstatus.objects(Q(client_email=email) |Q(requester_email=email)).first() is None:
        flash(
            "Your email is not registered on our database. please confirm your database",
            "danger",
        )
        return render_template("signup.html",role=role)

    user = User(username=username, email=email)
    user.hash_password(password=password)

    if user.save():
        flash("You were successfully registered.", "success")
        return render_template("login.html",role=role)
    else:
        flash("You were not registered. Please try again.", "danger")
        return render_template("signup.html",role=role)
    # return json.dumps(response)


def logout():
    try:
        logout_user()
    except Exception as ex:
        pass
    return redirect("/login")


@login_required
def lead():
    role=current_user.role
    cond = Q(client_email=current_user.email) |Q(requester_email=current_user.email)
    requests = Urlstatus.objects(cond).count()
    progress = Urlstatus.objects(cond & Q(google_status__ne="Removed")).count()
    completed = Urlstatus.objects(cond & Q(google_status="Removed")).count()
    canceled = Urlstatus.objects(cond & Q(status=None)).count()
    topoffender = list(
        Urlstatus.objects().aggregate(
            [
                {"$match": {"client_email": current_user.email}},
                {
                    "$project": {
                        "domain": {
                            "$substr": ["$url", 0, {"$indexOfBytes": ["$url", "/", 8]}]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$domain",
                        "count": {"$count": {}},
                    }
                },
                {"$sort": {"count": -1}},
                {"$limit": 3},
            ]
        )
    )
    topoffenders = []
    for t in topoffender:
        if t['_id'].find('//')>0:
            t["_id"] = t["_id"][t["_id"].index("//") + 2 : len(t["_id"])]
        topoffenders.append(t)
    app.logger.info(topoffenders)
    return render_template(
        "lead.html",
        requests=requests,
        progress=progress,
        completed=completed,
        canceled=canceled,
        topoffenders=(topoffenders),
        role=role
    )


@login_required
def results():
    cond = Q(client_email=current_user.email) |Q(requester_email=current_user.email)
    role = current_user.role
    requests = Urlstatus.objects(cond).count()
    progress = Urlstatus.objects(cond & Q(google_status__ne="Removed")).count()
    completed = Urlstatus.objects(cond & Q(google_status="Removed")).count()
    canceled = Urlstatus.objects(cond & Q(status=None)).count()
    current_month = datetime.now().strftime('/%m/%Y')
    
    requests_monthly = Urlstatus.objects(cond & Q(date__contains=current_month)).count()
    progress_monthly = Urlstatus.objects(cond & Q(google_status__ne="Removed") & Q(date__contains=current_month)).count()
    completed_monthly = Urlstatus.objects(cond & Q(google_status="Removed")  & Q(date__contains=current_month)).count()
    canceled_monthly = Urlstatus.objects(cond & Q(status=None)  & Q(date__contains=current_month)).count()
    completePct = getPctValue(completed_monthly, requests_monthly)
    updatingPct = getPctValue(progress_monthly, requests_monthly)
    livePct = 100 - completePct - updatingPct
    topoffender = list(
        Urlstatus.objects().aggregate(
            [
                {"$match": {"client_email": current_user.email}},
                {
                    "$project": {
                        "domain": {
                            "$substr": ["$url", 0, {"$indexOfBytes": ["$url", "/", 8]}]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$domain",
                        "count": {"$count": {}},
                    }
                },
                {"$sort": {"count": -1}},
                {"$limit": 3},
            ]
        )
    )
    topoffenders = []
    for t in topoffender:
        if t['_id'].find('//')>0:
            t["_id"] = t["_id"][t["_id"].index("//") + 2 : len(t["_id"])]
        topoffenders.append(t)
    app.logger.info(topoffenders)
    return render_template(
        "home.html",
        requests=requests,
        progress=progress,
        completed=completed,
        canceled=canceled,
        requestsPerMon=requests_monthly,
        progressPerMon=progress_monthly,
        completedPerMon=completed_monthly,
        livePct = str(livePct)+"%",
        removedPct = str(completePct)+"%",
        updatingPct = str(updatingPct)+"%",
        canceledPerMon=canceled_monthly,
        topoffenders=(topoffenders),
        role = role
    )

@login_required
def detail():
    role=current_user.role
    id = request.args.get('id')
    data = Urlstatus.objects(_id=ObjectId(id)).first()
    json_data= json.loads(data.to_json())

    if json_data['status'] =="Removed":
        json_data['site_color'] = "removed"
    elif json_data['status'] == 'Status Updating':
        json_data['site_color'] ='updating'
        json_data['status']="Updating"
    else:
        json_data['site_color'] ='live'

    if json_data['google_status'] =="Removed":
        json_data['google_color'] = "removed"
    elif json_data['google_status'] == 'Status Updating':
        json_data['google_color'] ='updating'
        json_data['google_status']="Updating"
    else:
        json_data['google_color'] ='live'
    if type(json_data['latest_update']['$date']) == int:
        json_data['latest_update']= datetime.fromtimestamp(json_data['latest_update']['$date']/1000).strftime('%m/%d/%Y')
    else:
        json_data['latest_update'] =json_data['latest_update']['$date']
    
    return render_template("detail.html",role=role,detail=json_data)

@login_required
def complete():
    cond = Q(client_email=current_user.email) |Q(requester_email=current_user.email)
    role = current_user.role
    requests = Urlstatus.objects(cond).count()
    progress = Urlstatus.objects(cond & Q(google_status__ne="Removed")).count()
    completed = Urlstatus.objects(cond & Q(google_status="Removed")).count()
    canceled = Urlstatus.objects(cond & Q(status=None)).count()
    current_month = datetime.now().strftime('/%m/%Y')
    requests_monthly = Urlstatus.objects(cond & Q(date__contains=current_month)).count()
    progress_monthly = Urlstatus.objects(cond & Q(google_status__ne="Removed") & Q(date__contains=current_month)).count()
    completed_monthly = Urlstatus.objects(cond & Q(google_status="Removed")  & Q(date__contains=current_month)).count()
    completePct = getPctValue(completed_monthly, requests_monthly)
    updatingPct = getPctValue(progress_monthly, requests_monthly)
    livePct = 100 - completePct - updatingPct
    # monthly_completed = Urlstatus.objects(cond & Q(status="Removed") & (Q(date__contains=current_month))).count()
    # monthly_google_completed = Urlstatus.objects(cond & Q(google_status="Removed") & (Q(date__contains=current_month))).count()
    topoffender = list(
        Urlstatus.objects().aggregate(
            [
                {"$match": {"client_email": current_user.email}},
                {
                    "$project": {
                        "domain": {
                            "$substr": ["$url", 0, {"$indexOfBytes": ["$url", "/", 8]}]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$domain",
                        "count": {"$count": {}},
                    }
                },
                {"$sort": {"count": -1}},
                {"$limit": 3},
            ]
        )
    )
    topoffenders = []
    for t in topoffender:
        if t['_id'].find('//')>0:
            t["_id"] = t["_id"][t["_id"].index("//") + 2 : len(t["_id"])]
        topoffenders.append(t)
    app.logger.info(topoffenders)
    return render_template(
        "complete.html",
        requests=requests,
        progress=progress,
        completed=completed,
        canceled=canceled,
        completePerMon = completed_monthly,
        requestPerMon =requests_monthly,
        livePct = str(livePct)+"%",
        removedPct = str(completePct)+"%",
        updatingPct = str(updatingPct)+"%",
        topoffenders=(topoffenders),
        role = role
    )

@login_required
def progress():
    cond = Q(client_email=current_user.email) |Q(requester_email=current_user.email)
    role = current_user.role
    requests = Urlstatus.objects(cond).count()
    progress = Urlstatus.objects(cond & Q(google_status__ne="Removed")).count()
    completed = Urlstatus.objects(cond & Q(google_status="Removed")).count()
    canceled = Urlstatus.objects(cond & Q(status=None)).count()
    current_month = datetime.now().strftime('/%m/%Y')
    requests_monthly = Urlstatus.objects(cond & Q(date__contains=current_month)).count()
    progress_monthly = Urlstatus.objects(cond & Q(google_status__ne="Removed") & Q(date__contains=current_month)).count()
    completed_monthly = Urlstatus.objects(cond & Q(google_status="Removed")  & Q(date__contains=current_month)).count()
    completePct = getPctValue(completed_monthly, requests_monthly)
    updatingPct = getPctValue(progress_monthly, requests_monthly)
    livePct = 100 - completePct - updatingPct
    # monthly_completed = Urlstatus.objects(cond & Q(status__ne="Removed") & (Q(date__contains=current_month))).count()
    # monthly_google_completed = Urlstatus.objects(cond & Q(google_status__ne="Removed") & (Q(date__contains=current_month))).count()
    topoffender = list(
        Urlstatus.objects().aggregate(
            [
                {"$match": {"client_email": current_user.email}},
                {
                    "$project": {
                        "domain": {
                            "$substr": ["$url", 0, {"$indexOfBytes": ["$url", "/", 8]}]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$domain",
                        "count": {"$count": {}},
                    }
                },
                {"$sort": {"count": -1}},
                {"$limit": 3},
            ]
        )
    )
    topoffenders = []
    for t in topoffender:
        if t['_id'].find('//')>0:
            t["_id"] = t["_id"][t["_id"].index("//") + 2 : len(t["_id"])]
        topoffenders.append(t)
    app.logger.info(topoffenders)
    return render_template(
        "progress.html",
        requests=requests,
        progress=progress,
        completed=completed,
        canceled=canceled,
        completePerMon = completed_monthly,
        requestPerMon =requests_monthly,
        livePct = str(livePct)+"%",
        removedPct = str(completePct)+"%",
        updatingPct = str(updatingPct)+"%",
        topoffenders=(topoffenders),
        role = role
    )

@login_required
def profile():
    userid = current_user.id
    role=current_user.role
    if request.method == "GET":
        return render_template("profile.html",role=role)

    response = {"success": False, "response": " "}
    username = request.form.get("username")
    phone = request.form.get("phone")
    user = current_user
    if user is None:
        flash("please login again", "danger")
        return render_template("profile.html",role=role)
    User.objects(pk=current_user.id).update_one(
        set__phone=phone, set__username=username
    )
    flash("Your information was updated successfully.", "success")
    return render_template("profile.html",role=role)


@login_required
def contact():
    role=current_user.role
    if request.method == "GET":
        return render_template("contact.html",role=role)
    send_emails(
        sender=app.config["MAIL_USERNAME"],
        subject=f"Contact to Internet Removals from {current_user.email}",
        msg=str(request.form.get("message")),
    )
    flash(
        "Your message was sent successfully. We will review your message asap. Thank you.",
        "success",
    )
    return render_template("contact.html",role=role)


@login_required
def submit():
    role=current_user.role
    if request.method == "GET":
        return render_template("submit.html",role=role)
    urls = request.form.get("url_input").split("\r\n")
    app.logger.info(urls)
    if urls is None:
        flash("Invalid URL.", "danger")
        return render_template("submit.html",role=role)
    
    your_email = request.form['email']
    client_name = request.form['username']
    client_email = current_user.email

    successes = []
    failures = []

    # Download contact file from URL
    contact_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRBOKV6T_ZT_9xVQtqYk4hGz53pclwE8XYKsD4KavIxgawYt2V8xf985fAoB_cT59r1ZCI-Ue1IX7A0/pub?output=xlsx'
    response = requests.get(contact_url)
    contact_file = io.BytesIO(response.content)

    # Read URLs from form input
    url_data = request.form['url_input']

    # Send emails and get successes and failures
    # #successes, failures = send_emails_dmca(url_data, contact_file, client_name)

    # Connect to MongoDB Atlas
    

    # Insert data into collection dmcaapp.dmcaapp
    
    data = {
        "requester_email": your_email,
        "client_name": client_name,
        "client_email": client_email,
        "url_data": url_data,
        "date": datetime.now().strftime('%d/%m/%Y'),
    }
    new_dmca = DmcaApp(requester_email=your_email,client_name=client_name,client_email=client_email,url_data=url_data,date=data['date'])
    if new_dmca.save():
        # flash("Successfully submitted.", "success")
        pass
    else:
        flash("Submittion failed. Please try again.", "danger")
        return render_template("submit.html",role=role)
            


    

    # Insert HTTP status of each URL into collection dmcaapp.urlstatus
    for url in url_data.strip().split("\n"):
        url = url.strip()
        if 'https://' not in url and 'http://' not in url:
            url = 'https://' + url
            
        if(is_valid_url(url)):

            try:
                response = requests.get(url)
                status_code = response.status_code
                data = {
                    "requester_email": your_email,
                    "client_name": client_name,
                    "client_email": client_email,
                    "url": url,
                    "status": str(status_code),
                    "date": datetime.now().strftime('%d/%m/%Y'),
                }
                matching_documents = Urlstatus.objects(url=url).first()

                
                if(matching_documents):
                    count = matching_documents['submission_count'] + 1
                    print(matching_documents)
                    id = matching_documents.id
                    print(id)
                    print(count)
                    Urlstatus.objects(pk=id).update(set__submission_count=count,set__latest_update = datetime.now())
                else:
                    new_url = Urlstatus(requester_email=your_email,client_email=client_email,client_name=client_name,url=url,status=str(status_code),date=data['date'])
                    new_url.save()
                    
            except Exception as e:
                print('error in urlstatus')
                print(e)

    # successes, failures = send_emails(url_data, contact_file, client_name)
    # send_emails(sender=app.config["MAIL_USERNAME"], subject=f"Request URLs from {current_user.email}", msg=urls)
    flash("Your submission was successed.", "success")
    return render_template("submit.html",role=role)


@login_required
def faq():
    role=current_user.role
    if request.method == "GET":
        faqs = Faq.objects()
        return render_template("faq.html", faqs=faqs,role=role)

    if request.form.get("_method") == "DELETE":
        id = request.form.get("id")
        Faq.objects(pk=id).delete()
        faqs = Faq.objects()
        return render_template("faq.html", faqs=faqs,role=role)

    question = request.form.get("question")
    id = request.form.get("id")
    answer = request.form.get("answer")
    if question:
        faq = Faq(
            client_email=current_user.email,
            requester_email="",
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            question=question,
            answer=answer,
        )
        flash("Your question is requested successfully.", "success")
        faq.save()
        faqs = Faq.objects()
        return render_template("faq.html", faqs=faqs,role=role)
    if id:
        Faq.objects(id=id).update(answer=answer)
        flash("Your question is requested successfully.", "success")
        faqs = Faq.objects()
        return render_template("faq.html", faqs=faqs,role=role)


@lm.user_loader
def user_loader(user_id):
    return User.objects(pk=user_id).first()


@lm.request_loader
def load_user_from_request(request):
    api_key = request.headers.get("Authorization")
    if api_key:
        api_key = api_key.replace("Basic ", "", 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        userFromSession = Session.objects(session_id=api_key).first()
        if userFromSession:
            user = User.objects(pk=userFromSession["userId"])
            user_obj = user
            if user_obj:
                return user_obj
            else:
                return None
        else:
            return None

@login_required
def report():
    role=current_user['role']
    return render_template("reports.html",role=role)

@login_required
def staffs():
    role=current_user['role']
    return render_template("staffs.html",role=role)



def send_emails(sender, subject, msg):
    message = MIMEMultipart()
    message["Subject"] = "Contact to InternetRemovals"
    message["From"] = sender
    message["To"] = ["team@internetremovals.com"]
    msg = '\n'.join(msg)
    body = f"""
        From: {sender}
        Subject: {subject}
        {msg}"""

    message.attach(MIMEText(body, "plain"))
    context = ssl.create_default_context()
    with smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]) as server:
        server.ehlo()
        server.starttls()
        server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
        try:
            server.sendmail(sender, message["To"], body)
        except smtplib.SMTPException as e:
            print(f"An error occurred while sending email: {e}")


    
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def send_emails_dmca(url_data, contact_file, client_name):
    # Load contact file
    contact_df = pd.read_excel(contact_file, engine='openpyxl')

    # Extract domain names from contact file
    domains = contact_df['domain name'].tolist()

    # Create dictionary to store URLs by domain
    urls_by_domain = {d: [] for d in domains}

    # Initialize variables to store successes and failures
    successes = []
    failures = []

    # Loop through each URL in the URL data
    for url in url_data.strip().split("\n"):
        # Extract the domain from the URL
        domain = '.'.join(url.split('//')[-1].split('/')[0].replace('www.', '').split('.'))

        # Check if the domain exists in the contact file
        if domain in domains:
            # Add the URL to the list of URLs for the domain
            urls_by_domain[domain].append(url)
        else:
            failures.append(url)

    new_line = "<br>"

    # Loop through each domain
    for domain, urls in urls_by_domain.items():
        # Check if there are any URLs for the domain
        if len(urls) > 0:
            # Compose email
            message = MIMEMultipart()
            message["Subject"] = f"DMCA Removal Request - {client_name}"
            message["From"] = "Internet Removals DMCA Team"
            message["To"] = ", ".join(
                contact_df[contact_df['domain name'] == domain]['email'].tolist())
            body = f"""<html><body><p>Dear Sir or Madam,</p>
<p>We act as agents for {client_name}. Your website, or a website that your company is hosting, is infringing on a copyright-protected file that our client is the legal rights owner of. These files were copied onto your servers without our client's permission.</br>
<p>The unauthorized and infringing copies are located at:</p>
{new_line.join(urls)}
<p>This email constitutes an official notification of the infringement and our client's legal request that you immediately remove or disable access to the infringing material, and ensure that the user refrains from any unauthorized use or sharing of our client's copyrighted materials in the future.</p>
<p>If you are hosting the image for another party, we request that you immediately notify the infringer of this notice, inform them of their duty to remove the infringing material immediately, ensure the material is removed, and notify them to cease any further posting of infringing material to your server in the future.</p>
<p>Under Section 512(c) of the Digital Millennium Copyright Act (DMCA), you are to expediently remove the infringing work upon receipt of this notice. The Online Copyright Infringement Liability Limitation Act may grant service providers immunity from liability so long as it investigates and corrects this copyright violation in a timely manner. Noncompliance may result in the loss of your statutory immunity for the infringement under the Act.</p>
<p>I have a good faith belief that use of the copyrighted materials described above as allegedly infringing is not authorized by the copyright owner, its agent, or the law. </p>
<br>
<p>The information provided in the notification is accurate to the best of my knowledge and belief. Nothing in this notification shall serve as a waiver of any rights or remedies, of our client, with respect to this alleged infringement, all of which are expressly reserved.</p>
<p>I swear, under penalty of perjury, that I am the copyright owner or am authorized to act on behalf of the owner of an exclusive right that is allegedly infringed.</p>
<p>Kind Regards,<br>
For {client_name} (by electronic signature)<br>
Ethan Czarfost<br>
+1300039196<br>
team@internetremovals.com<br>
Level 3, 130 Bundall Road<br>
Bundall 4217<br>
Australia
<p>"Managing DMCA notices and compliance is difficult. If you want help with this, enquire about our DMCA Agent Services. We process DMCA notices on your behalf and ensure compliance."</p>
</body></html>"""

            message.attach(MIMEText(body, "html"))

            # Send email
            context = ssl.create_default_context()
            smtp_server = "smtp.gmail.com"
            from_address = "internetremovalsdmcaagent3@gmail.com"
            password = "pnuafzhqygffupxg"

            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, 587) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(from_address, password)

                try:
                    server.sendmail("team@internetremovals.com", message["To"].split(", "),
                                    message.as_string())
                    successes.extend(urls)
                except smtplib.SMTPException as e:
                    failures.extend(urls)
                    print(f"An error occurred while sending email: {e}")

    # Return successes and failures
    return successes, failures

def getPctValue(value,total):
    return math.floor(value *100 /total) 