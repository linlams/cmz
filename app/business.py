# -*- coding: utf-8 -*-
from flask import request
from flask import Blueprint
from conf.settings import db
from util import json_response

app = Blueprint('business_mgmt', __name__)
route = app.route


@route('/', methods=['GET'])
@json_response
def get_all_businesses():
    return db.business.find()


@route('/<business_name>', methods=['POST'])
@json_response
def save_business(business_name):
    business_str = request.get_data()
    print business_str
    return db.business.find()
