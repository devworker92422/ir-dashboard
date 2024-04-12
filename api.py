# -*- coding: utf-8 -*-
# @Author: Tahiana
# @Date:   2023-03-23 13:08:19
# @Last Modified by:   Tahiana
# @Last Modified time: 2023-03-28 14:15:54

from os import write
from app import app, lm
import json_normalize
import xlsxwriter
from flask import (
    Flask,
    flash,
    render_template,
    request,
    session,
    redirect,
    url_for,
    send_file,
)
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.models.urlstatus import Urlstatus
from app.models.lead import Lead
from app.models.preq import Preq
from app.models.staff import Staff
from app.models.xero import Xero
from bson import json_util, ObjectId
import json
import base64
from mongoengine.queryset.visitor import Q , QCombination
import re
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta
import numpy as np

# import pdfkit

@login_required
def getClients():
    cond =  (Q(client_email=current_user.email) |Q(requester_email=current_user.email) ) 
    docs = (Urlstatus.objects(cond))
    clients = []
    for doc in docs:
        #doc = json.loads(doc.to_json())
        if(doc['client_name'] not in clients):
            clients.append(doc['client_name'])
    return json.dumps({'success':True,'results':clients})

def qcombination_to_dict(qcombination):
    if isinstance(qcombination, QCombination):
        op = qcombination.__class__.__name__
        children = [qcombination_to_dict(child) for child in qcombination.children]
        return {op: children}
    elif isinstance(qcombination, Q):
        return qcombination.as_dict()
    else:
        raise ValueError("Unsupported type in QCombination")

@login_required
def urls():
    q = request.args.to_dict()
    search_key = ''
    if q.get('search[value]') != None:
        search_key = str(q.get('search[value]'))
    google_status_key = q.get("columns[7][search][value]")
    status_key = q.get("columns[6][search][value]")
    client_name_key = q.get("columns[3][search][value]")
    limit = int(q.get("length", 10))
    page = int(q.get("start", 0)) / limit + 1
    field = q.get(f'columns[{q.get("order[0][column]")}][name]')
    d = f'{"+" if q.get("order[0][dir]") == "desc" else "-"}'
    d = 1 if q.get("order[0][dir]") == "desc" else -1
    searcg_email = current_user.email
    cond =  (Q(client_email=searcg_email) |Q(requester_email=searcg_email) )& (Q(client_name__contains=search_key) | Q(url__contains=search_key) | Q(requester_email__contains=search_key) | Q(client_email__contains=search_key))
    if google_status_key:
        cond = cond & Q(google_status=google_status_key)
    if status_key:
        cond = cond & Q(status=status_key)
    if client_name_key:
        cond = cond & Q(client_name=client_name_key)
    app.logger.info(cond)
    total = Urlstatus.objects(cond).count()
    if total < page * limit and total > (page - 1) * limit:
        limit = int(total - (page - 1) * limit)
    pipeline = [
        {"$group": {
            "_id": "$url",
            "total_count" : {"$sum" : 1},
            "max_submission_count": {"$max": "$submission_count"},
            "document": {"$first": "$$ROOT"}
        }},
        {"$replaceRoot": {"newRoot": "$document"}},
        {
            "$project" : {
                "_id" : 1,
                "client_name" : 1,
                "client_email" : 1,
                "url" : 1,
                "status"  :1,
                "google_status" : 1,
                "submission_count" : 1,
                "date_checked" : 1,
                "date" : 1,
                "requester_email" : 1,
            }
        },
        {"$unwind" : "$url"},
        {"$sort": {field: d}},
        {
            "$facet": {
            "paginatedResults": [{ "$skip": (page-1)*limit }, { "$limit": limit }],
            "totalCount": [
                {
                "$count": 'count'
                }
            ]
        }
    }
    ] 
    result = (Urlstatus.objects(cond).aggregate(pipeline,allowDiskUse=True))
    data = list(result)
    try:
        total_count = data[0]['totalCount'][0]['count']
    except:
        total_count = 0
    data = data[0]['paginatedResults']
    records = []
    for d in data:
        record = d
        record["id"] = str(record["_id"])
        try:
            if np.isnan(record['google_status']):
                record['google_status'] = 'Status Updating'
        except:
            pass
        
        try:
            if np.isnan(record['client_name']):
                record['client_name'] = 'Unknown'
        except:
            pass
        records.append(record)
    response = {
        "draw": q.get("draw"),
        "recordsTotal": total,
        "recordsFiltered": int(total_count),
        "data": records,
    }
    return json.dumps(response,default=json_util.default)

@login_required
def urls_completed():
    q = request.args.to_dict()
    search_key = ''
    if q.get('search[value]') != None:
        search_key = str(q.get('search[value]'))
    google_status_key = q.get("columns[7][search][value]")
    status_key = q.get("columns[6][search][value]")
    client_name_key = q.get("columns[3][search][value]")
    limit = int(q.get("length", 10))
    page = int(q.get("start", 0)) / limit + 1
    field = q.get(f'columns[{q.get("order[0][column]")}][name]')
    d = f'{"+" if q.get("order[0][dir]") == "desc" else "-"}'
    d = 1 if q.get("order[0][dir]") == "desc" else -1
    searcg_email = current_user.email
    cond =  (Q(client_email=searcg_email) |Q(requester_email=searcg_email) )& (Q(client_name__contains=search_key) | Q(url__contains=search_key) | Q(requester_email__contains=search_key) | Q(client_email__contains=search_key)) 
    if google_status_key:
        cond = cond & Q(google_status=google_status_key)
    if status_key:
        cond = cond & Q(status=status_key)
    if client_name_key:
        cond = cond & Q(client_name=client_name_key)
    app.logger.info(cond)
    total = Urlstatus.objects(cond).count()
    current_month = datetime.now().strftime('/%m/%Y')
    monthly_completed = Urlstatus.objects(cond & Q(status="Removed") & (Q(date__contains=current_month))).count()
    monthly_google_completed = Urlstatus.objects(cond & Q(google_status="Removed") & (Q(date__contains=current_month))).count()
    if total < page * limit and total > (page - 1) * limit:
        limit = int(total - (page - 1) * limit)
    pipeline = [
        {"$group": {
            "_id": "$url",
            "total_count" : {"$sum" : 1},
            "max_submission_count": {"$max": "$submission_count"},
            "document": {"$first": "$$ROOT"}
        }},
        {"$replaceRoot": {"newRoot": "$document"}},
        {
            "$project" : {
                "_id" : 1,
                "client_name" : 1,
                "client_email" : 1,
                "url" : 1,
                "status"  :1,
                "google_status" : 1,
                "submission_count" : 1,
                "date_checked" : 1,
                "date" : 1,
                "requester_email" : 1,
            }
        },
        {"$unwind" : "$url"},
        
        {"$sort": {field: d}},
        {
            "$facet": {
            "paginatedResults": [{ "$skip": (page-1)*limit }, { "$limit": limit }],
            "totalCount": [
                {
                "$count": 'count'
                }
            ]
        }
    }
    ]
    result = (Urlstatus.objects(cond &(Q(status="Removed"))).aggregate(pipeline,allowDiskUse=True))
    data = list(result)
    print(data[0])
    try:
        total_count = data[0]['totalCount'][0]['count']
    except:
        total_count = 0
    data = data[0]['paginatedResults']
    records = []
    for d in data:
        record = d
        record["id"] = str(record["_id"])
        try:
            if np.isnan(record['google_status']):
                record['google_status'] = 'Status Updating'
        except:
            pass
        
        try:
            if np.isnan(record['client_name']):
                record['client_name'] = 'Unknown'
        except:
            pass
        records.append(record)
    response = {
        "draw": q.get("draw"),
        "recordsTotal": total,
        "recordsFiltered": int(total_count),
        "data": records,
        "monthly_completed" : monthly_completed,
        "monthly_google_completed" : monthly_google_completed,
    }
    return json.dumps(response,default=json_util.default)

@login_required
def urls_in_progress():
    q = request.args.to_dict()
    search_key = ''
    if q.get('search[value]') != None:
        search_key = str(q.get('search[value]'))
    google_status_key = q.get("columns[7][search][value]")
    status_key = q.get("columns[6][search][value]")
    client_name_key = q.get("columns[3][search][value]")
    limit = int(q.get("length", 10))
    page = int(q.get("start", 0)) / limit + 1
    field = q.get(f'columns[{q.get("order[0][column]")}][name]')
    d = f'{"+" if q.get("order[0][dir]") == "desc" else "-"}'
    d = 1 if q.get("order[0][dir]") == "desc" else -1
    searcg_email = current_user.email
    cond =  (Q(client_email=searcg_email) |Q(requester_email=searcg_email) )& (Q(client_name__contains=search_key) | Q(url__contains=search_key) | Q(requester_email__contains=search_key) | Q(client_email__contains=search_key))
    if google_status_key:
        cond = cond & Q(google_status=google_status_key)
    if status_key:
        cond = cond & Q(status=status_key)
    if client_name_key:
        cond = cond & Q(client_name=client_name_key)
    app.logger.info(cond)
    total = Urlstatus.objects(cond).count()
    current_month = datetime.now().strftime('/%m/%Y')
    monthly_completed = Urlstatus.objects(cond & Q(status__ne="Removed") & (Q(date__contains=current_month))).count()
    monthly_google_completed = Urlstatus.objects(cond & Q(google_status__ne="Removed") & (Q(date__contains=current_month))).count()
    if total < page * limit and total > (page - 1) * limit:
        limit = int(total - (page - 1) * limit)
    pipeline = [
        {"$group": {
            "_id": "$url",
            "total_count" : {"$sum" : 1},
            "max_submission_count": {"$max": "$submission_count"},
            "document": {"$first": "$$ROOT"}
        }},
        {"$replaceRoot": {"newRoot": "$document"}},
        {
            "$project" : {
                "_id" : 1,
                "client_name" : 1,
                "client_email" : 1,
                "url" : 1,
                "status"  :1,
                "google_status" : 1,
                "submission_count" : 1,
                "date_checked" : 1,
                "date" : 1,
                "requester_email" : 1,
            }
        },
        {"$unwind" : "$url"},
        {"$sort": {field: d}},
        {
            "$facet": {
            "paginatedResults": [{ "$skip": (page-1)*limit }, { "$limit": limit }],
            "totalCount": [
                {
                "$count": 'count'
                }
            ]
        }
    }
    ]   
    result = (Urlstatus.objects(cond &(Q(status__ne="Removed"))).aggregate(pipeline,allowDiskUse=True))
    data = list(result)
    print(data[0])
    try:
        total_count = data[0]['totalCount'][0]['count']
    except:
        total_count = 0
    data = data[0]['paginatedResults']
    records = []
    for d in data:
        record = d
        record["id"] = str(record["_id"])
        try:
            if np.isnan(record['google_status']):
                record['google_status'] = 'Status Updating'
        except:
            pass
        
        try:
            if np.isnan(record['client_name']):
                record['client_name'] = 'Unknown'
        except:
            pass
        records.append(record)
    response = {
        "draw": q.get("draw"),
        "recordsTotal": total,
        "recordsFiltered": int(total_count),
        "data": records,
        "monthly_progress" : monthly_completed,
        "monthly_google_progress" : monthly_google_completed,
    }
    return json.dumps(response,default=json_util.default)


@login_required
def leads():
    q = request.args.to_dict()

    search_key = re.compile(str(q.get("search[value]"))) 

    limit = int(q.get("length", 10))
    page = int(q.get("start", 0)) / limit + 1

    field = q.get(f'columns[{q.get("order[0][column]")}][name]')
    d = f'{"+" if q.get("order[0][dir]") == "asc" else "-"}'

    cond =  Q(name=search_key)  
    total = Lead.objects(cond).count()

    if total < page * limit and total > (page - 1) * limit:
        limit = int(total - (page - 1) * limit)

    data = (
        Lead.objects(cond)
        # .order_by(f"{d}{field}")
        .paginate(page=page, per_page=limit)
    )

    records = []
    for d in data.items:
        record = json.loads(d.to_json())
        record["id"] = record["_id"]["$oid"]
        records.append(record)
    response = {
        "draw": q.get("draw"),
        "recordsTotal": total,
        "recordsFiltered": data.total,
        "data": records,
    }
    return json.dumps(response)

@login_required
def export():
    q = request.args.to_dict()

    search_key = re.compile(str(q.get("search[value]")))
    google_status_key = q.get("columns[7][search][value]")
    status_key = q.get("columns[6][search][value]") 

    field = q.get(f'columns[{q.get("order[0][column]")}][name]')
    d = f'{"+" if q.get("order[0][dir]") == "asc" else "-"}'

    cond =  (Q(client_email=current_user.email) |Q(requester_email=current_user.email) )& (Q(url=search_key) | Q(requester_email=search_key) | Q(client_email=search_key))
    if google_status_key:
        cond = cond & Q(google_status=google_status_key)
    if status_key:
        status_key = status_key.split("-")
        cond = cond & Q(status__gte=status_key[0]) & Q(status__lt=status_key[1]) 
    urls = (
        Urlstatus.objects(cond)
        .order_by(f"{d}{field}") 
    )
    urllist = [] 
    for url in urls:
      l = json.loads(url.to_json())
      del l["_id"]
      urllist.append(l)
    df = pd.DataFrame(urllist)
    df.index = df.index + 1
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, startrow=0, merge_cells=False, sheet_name="url_status", index_label="No")
    writer.close()
    output.seek(0)
    return send_file(output, download_name="url_status.xlsx", as_attachment=True)

@login_required
def getStaffData():
    staff_dict = {
        'Kavita Sharma' : 'Kavita',
        'Dion Reisman' : 'Dion',
        'Zach Featherstone' : 'Zach',
        '' : '*****'
    }
    q = request.args.to_dict()
    search_key = str(q.get("search[value]")).lower()
    limit = int(q.get("length", 10))
    page = int(q.get("start", 0)) / limit + 1
    view_mode = int(q.get("display"))
    date_range = int(q.get("dateRange"))

    print(view_mode,page, limit)

    if(date_range == 0):
        start_date = datetime(2000,1,1)
        end_date = datetime(9999,12,31)
    elif(date_range == 1):
        end_date = datetime.today()
        start_date = end_date - timedelta(days=1)
        end_date = datetime(end_date.year, end_date.month, end_date.day,23,59,59)
    elif(date_range == 7):
        end_date = datetime.today()
        weekday = datetime.today().weekday()
        start_date = end_date - timedelta(days=weekday)
        start_date = datetime(start_date.year, start_date.month, start_date.day,0,0,0)
        end_date = datetime(end_date.year, end_date.month, end_date.day,23,59,59)
    else:
        end_date = datetime.today()
        dayofmonth = datetime.today().day
        start_date = end_date - timedelta(days=(dayofmonth - 1))
        start_date = datetime(start_date.year, start_date.month, start_date.day,0,0,0)
        end_date = datetime(end_date.year, end_date.month, end_date.day,23,59,59)


    # params=json.loads(request.data)
    # view_mode=int(params['mode']) 
    print(start_date, end_date)
    role=current_user.role
    allStaff= [
                {"$match": 
                    {'date': {
                        '$gte': start_date,
                        '$lte': end_date,
                    }},
                },
                {
                    "$project": {"_id":1,"contact_email":1,"contact_first_name":1,"total_url":1,"region":1 ,"proposal_id" : 1,"full_name" : 1}
                },
                {
                    "$group": {
                        "_id": "$contact_email",
                        "name":{"$first":"$full_name"},
                        "region":{"$first":"$region"},
                        "count": {"$count": {}},
                    }
                },
                {"$sort": {"count": -1}}
                ]
    staff = [
                 {"$match": {
                    "$and" : [
                        {"contact_email": current_user['email']},
                        {'date': {
                            '$gte': start_date,
                            '$lte': end_date,
                        }},
                        ]
                 }
                },
                {
                    "$project": {"_id":1,"contact_email":1,"contact_first_name":1,"total_url":1,"region":1 ,"proposal_id" : 1,"full_name" : 1}
                },
                {
                    "$group": {
                        "_id": "$contact_email",
                        "name":{"$first":"$full_name"},
                        "region":{"$first":"$region"},
                        "count": {"$count": {}},
                    }
                },
                {"$sort": {"count": -1}}
            ]
    staffCountry = [
                 {"$match": {
                    "$and" : [
                        {"contact_email": current_user['email']},
                        {'date': {
                            '$gte': start_date,
                            '$lte': end_date,
                        }}
                        ]
                 }
                },
                {
                    "$project": {"_id":1,"contact_email":1,"contact_first_name":1,"total_url":1,"region":1 ,"proposal_id" : 1,"full_name" : 1}
                },
                {
                    "$group": {
                        "_id": "$region",
                        "count": {"$count": {}},
                    }
                },
                {"$sort": {"count": -1}}
            ]
    allCountry = [
                {"$match": {'date': {
                        '$gte': start_date,
                        '$lte': end_date,
                    }},
                },
                {
                    "$project": {"_id":1,"contact_email":1,"contact_first_name":1,"total_url":1,"region":1 ,"proposal_id" : 1,"full_name" : 1}
                },
                {
                    "$group": {
                        "_id": "$region",
                        "count": {"$count": {}},
                    }
                },
                {"$sort": {"count": -1}}
            ]
    adminCountry = [
                {"$match": {
                    "$and" : [
                        {"region": current_user['region']},
                        {'date': {
                            '$gte': start_date,
                            '$lte': end_date,
                        }},
                    ]
                    }
                },
                {
                    "$project": {"_id":1,"contact_email":1,"contact_first_name":1,"total_url":1,"region":1 ,"proposal_id" : 1,"full_name" : 1}
                },
                {
                    "$group": {
                        "_id": "$region",
                        "count": {"$count": {}},
                    }
                },
                {"$sort": {"count": -1}}
            ]
    countryStaff = [
                    {"$match": {
                    "$and" : [
                        {"region": current_user['region']},
                        {'date': {
                            '$gte': start_date,
                            '$lte': end_date,
                        }},
                        ]
                        }
                    },
                    {
                        "$project": {"_id":1,"contact_email":1,"contact_first_name":1,"total_url":1,"region":1 ,"proposal_id" : 1,"full_name" : 1}
                    },
                    {
                        "$group": {
                            "_id": "$contact_email",
                            "name":{"$first":"$full_name"},
                            "region":{"$first":"$region"},
                            "count": {"$count": {}},
                        }
                    },
                    {"$sort": {"count": -1}}
                ]
    
    if role==1:
        if view_mode == 1:
            staff_data = Preq.objects().aggregate(allCountry)
        else:
            staff_data = Preq.objects().aggregate(allStaff)        
    if role == 2:
        if view_mode == 1:
            staff_data = Preq.objects().aggregate(adminCountry)
        else:
            staff_data = Preq.objects().aggregate(countryStaff)
    if role == 3:
        if view_mode == 1:
            staff_data = Preq.objects().aggregate(staffCountry)
        else:
            staff_data = Preq.objects().aggregate(staff)
        # else:
        
    staff_data = list(staff_data)
    
    total = len(staff_data)
    results = []
    if(view_mode == 1):
        for item in staff_data:
            index = staff_data.index(item)
            print(index)
            if(index < page*limit and index >= (page-1)*limit):
                if(search_key in item['_id'].lower() or search_key == ""):
                    invoice_pipeline = [
                        {"$match": {
                            "$and" : [
                                {"region": item['_id']},
                                {'date': {
                                    '$gte': start_date,
                                    '$lte': end_date,
                                }} 
                                ]
                        }
                        },
                        {
                            "$group": {
                                "_id": "$region",
                                "count": {"$count": {}},
                                "total_payment" : {"$sum" : "$amount_paid"}
                            }
                        },
                    ]
                    invoice_data = list(Xero.objects().aggregate(invoice_pipeline))
                    invoice_count = invoice_data[0]['count'] if(len(invoice_data) > 0) else 0
                    total_payment = invoice_data[0]['total_payment'] if(len(invoice_data) > 0) else 0
                    results.append({
                        'id' : item['_id'],
                        'country' : item['_id'],
                        'staff_email' : '',
                        'staff_name' : '',
                        'proposals_issued' : item['count'],
                        'invoices_issued' : invoice_count,
                        'payments_collected' : total_payment,
                    })
    else:
        for item in staff_data:
            index = staff_data.index(item)
            if(index < page*limit and index >= (page-1)*limit):
                if(search_key in item['_id'].lower() or search_key in item['name'].lower() or search_key == ""):
                    staff = Staff.objects(Q(email=item['_id'])).first()
                    try:
                        staff_name = staff.name
                    except:
                        staff_name = ''
                    staff_first_name = staff_dict[staff_name]
                    print(staff_first_name)
                    invoice_pipeline = [
                        {"$match": {
                            "$and" : [
                                {"staff_name": staff_first_name},
                                {'date': {
                                '$gte': start_date,
                                '$lte': end_date,
                            }},]
                            }
                        },
                        {
                            "$group": {
                                "_id": "$staff_name",
                                "count": {"$count": {}},
                                "total_payment" : {"$sum" : "$amount_paid"}
                            }
                        },
                    ]
                    invoice_data = list(Xero.objects().aggregate(invoice_pipeline))
                    invoice_count = invoice_data[0]['count'] if(len(invoice_data) > 0) else 0
                    total_payment = invoice_data[0]['total_payment'] if(len(invoice_data) > 0) else 0
                    results.append({
                        'id' : item['_id'],
                        'country' :item['region'],
                        'staff_email' : item['_id'],
                        'staff_name' : staff_name,
                        'proposals_issued' : item['count'],
                        'invoices_issued' : invoice_count,

                        'payments_collected' : total_payment,
                    })
    print(results)

    response = {
        "draw": q.get("draw"),
        "recordsTotal": total,
        "recordsFiltered": len(results),
        "data": results,
    }
    return json.dumps(response)

@login_required
def getAllStaffs():
    q = request.args.to_dict()
    search_key = re.compile(str(q.get("search[value]"))) 

    limit = int(q.get("length", 10))
    page = int(q.get("start", 0)) / limit + 1

    field = q.get(f'columns[{q.get("order[0][column]")}][name]')
    d = f'{"+" if q.get("order[0][dir]") == "asc" else "-"}'

    cond =  Q(name=search_key) | Q(email=search_key)  
    

    data = (
        Staff.objects(cond)
        # .order_by(f"{d}{field}")
        .paginate(page=page, per_page=limit)
    )

    role = current_user.role
    if(role == 1):
        total = Staff.objects(cond).count()
        if total < page * limit and total > (page - 1) * limit:
            limit = int(total - (page - 1) * limit)
        data = (
            Staff.objects(cond)
            .paginate(page=page, per_page=limit)
        )
    elif(role == 2):
        region = current_user.region
        cond = cond & Q(region=region)
        total = Staff.objects(cond).count()
        if total < page * limit and total > (page - 1) * limit:
            limit = int(total - (page - 1) * limit)
        data = (
            Staff.objects(cond)
            .paginate(page=page, per_page=limit)
        )
    else:
        return
    
    records = []
    
    for d in data.items:
        record = json.loads(d.to_json())
        record["id"] = record["_id"]["$oid"]
        records.append(record)

    response = {
        "draw": q.get("draw"),
        "recordsTotal": total,
        "recordsFiltered": data.total,
        "data": records,
    }
    return json.dumps(response)

@login_required
def saveStaff():
    data = json.loads(request.data)
    id = data['id']
    name = data['name']
    role = data['role']
    email = data['email']
    region = data['region']
    Staff.objects(pk=id).update_one(
        set__name=name ,
        set__role=role ,
        set__email=email,
        set__region=region , 
    )
    User.objects(Q(email=email)).update_one(set__role=role)
    return 'success'

@login_required
def removeStaff():
    data = json.loads(request.data)
    id = data['id']
    Staff.objects(pk=id).delete()
    return 'success'

@login_required
def addNewStaff():
    data = json.loads(request.data)
    email = data['email']
    if(Staff.objects(Q(email=email)).count() > 0):
        return json.dumps({'status' : 'fail','message' : 'Email already exists'})
    else:
        staff = Staff(name=data['name'], email=email,role=data['role'],region=data['region'])
        User.objects(Q(email=email)).update_one(set__role=data['role'])
        if staff.save():
            return json.dumps({'status' : 'success'})
        else:
            return json.dumps({'status' : 'fail','message' : 'Failed to add new staff. Please try again.'})
        
# def htmlToPdf():
#     data = json.loads(request.data)
#     url = data['url']
#     pdfkit.from_url(url, '/result.pdf')
#     return send_file('/result.pdf',as_attachment=True)

@login_required
def updateStatus():
    data = json.loads(request.data)
    id = data['id']
    status = data['status']
    Urlstatus.objects(id=ObjectId(id)).update_one(set__status=status)
    return 'success'

@login_required
def updateGoogleStatus():
    data = json.loads(request.data)
    id = data['id']
    status = data['status']
    Urlstatus.objects(id=ObjectId(id)).update_one(set__google_status=status)
    return 'success'

@login_required
def feedback():
    msg = request.form.get('feedback')
    print(msg)
    
    return msg