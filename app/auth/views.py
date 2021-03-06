# -*- coding: utf-8 -*-
from flask import render_template, redirect, request, url_for
from flask.ext.login import current_user, login_user, logout_user
import urllib2
import json
from config import KSSO_LOCAL_URL, KSSO_SERVER_URL
from . import auth
from ..models import User
from .. import db


@auth.route('/login')
def login():
    token = request.args.get('t')

    if token:
        req = urllib2.Request('%s/verify?t=%s&format=json' % (KSSO_SERVER_URL, token))
        req.add_header('Referer', KSSO_LOCAL_URL)
        sss = urllib2.urlopen(req)
        result = json.loads(sss.read())

        if result['result'] and result['detail']['departmentId__departmentName'] == u'运维部':
            username = result['user']
            user = User.query.filter_by(username=username).first()
            if user is None:
                user = User(username=username)
                db.session.add(user)
                db.session.commit()
            login_user(user)
            return redirect(KSSO_LOCAL_URL)
        else:
            return u"目前只能有运维部的童鞋可以登录些系统。你不是能正常登录此网站，请联系系统管理员"

    else:
        return redirect(
            "{KSSO_SERVER_URL}/login?forward={KSSO_LOCAL_URL}{auth_login}".format(
                # **dict(
                    KSSO_SERVER_URL=KSSO_SERVER_URL,
                    KSSO_LOCAL_URL=KSSO_LOCAL_URL,
                    auth_login=url_for('auth.login'),
                # )
            )
        )


@auth.route('/logout')
def logout():
    logout_user()
    return redirect("%s/logout?forward=%s" % (KSSO_SERVER_URL, KSSO_LOCAL_URL))
