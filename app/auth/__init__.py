# -*- coding: utf-8 -*-
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
# from settings import KSSO_SERVER_URL, KSSO_LOCAL_URL
# from flask import session, redirect, Blueprint, request as req
# import urllib2
# import functools
# import json
# 
# app = Blueprint('auth', __name__, template_folder='templates')
# 
# 
# def login_required(func):
#     @functools.wraps(func)
#     def _(*args, **kwargs):
#         # 判断是否登录
#         if not session.get('user'):
#             return redirect("%s/login?forward=%s/auth/login" % (KSSO_SERVER_URL, KSSO_LOCAL_URL))
#         else:
#             return func(*args, **kwargs)
#     return _
# 
# 
# @app.route('/login')
# def login():
#     ticket = req.values.get('t')
#     if ticket:
#         request = urllib2.Request('%s/verify?t=%s&format=json' % (KSSO_SERVER_URL, ticket))
#         # print "TOKEN:", ticket
#         request.add_header('Referer', KSSO_LOCAL_URL)
#         sss = urllib2.urlopen(request)
#         result = json.loads(sss.read())
# 
#         if result['result'] and result['detail']['departmentId__departmentName'] == u'运维部':
#             # {"result": true, "message": "Success", "user": "wangxulin", "detail": {"phone": 18611160027, "departmentId__enName": "operation", "departmentId__departmentName": "\\u8fd0\\u7ef4\\u90e8", "email": "wangxulin@conew.com"}, "t": "cbdc9e01430939f7b29cbfd676ba54b8-6c74913a-6371-3fa2-92aa-2247a8db3923"}
#             session['user'] = {
#                 "username": result['user'],
#                 "phone": result['detail']['phone'],
#                 "department": {
#                     "name": result['detail']['departmentId__departmentName'],
#                     "en_name": result['detail']['departmentId__enName']
#                 },
#                 "email": result['detail']['email']
#             }
#             return redirect(KSSO_LOCAL_URL)
# 
#     return redirect("%s/sorry" % (KSSO_LOCAL_URL))
#     # return redirect("%s/login?forward=%s/login" % (KSSO_SERVER_URL, KSSO_LOCAL_URL))
# 
# 
# @app.route('/logout')
# def logout():
#     del session['user']
#     return redirect("%s/logout?forward=%s" % (KSSO_SERVER_URL, KSSO_LOCAL_URL))
# 

