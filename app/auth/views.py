# -*- coding: utf-8 -*-
from flask import render_template, redirect, request, url_for
from flask.ext.login import current_user, login_user, logout_user
import urllib2
import json
from config import KSSO_LOCAL_URL, KSSO_SERVER_URL
from . import auth
from ..models import User


#import pdb; pdb.set_trace()

@auth.route('/login')
def login():
    token = request.args.get('t')

    if token:
        req = urllib2.Request('%s/verify?t=%s&format=json' % (KSSO_SERVER_URL, token))
        req.add_header('Referer', KSSO_LOCAL_URL)
        sss = urllib2.urlopen(req)
        result = json.loads(sss.read())
        import pdb; pdb.set_trace()

        if result['result'] and result['detail']['departmentId__departmentName'] == u'运维部':
            # session['user'] = {
            #     "username": result['user'],
            #     "phone": result['detail']['phone'],
            #     "department": {
            #         "name": result['detail']['departmentId__departmentName'],
            #         "en_name": result['detail']['departmentId__enName']
            #     },
            #     "email": result['detail']['email']
            # }
            user = User.query.filter_by(username=result['user']).first()
            login_user(user)
            return redirect(KSSO_LOCAL_URL)
        else:
            return "ABC"

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
    #return redirect(request.args.get('next') or url_for('main.index'))


@auth.route('/logout')
def logout():
    logout_user()
    return redirect('/')
    #return redirect(request.args.get('next') or url_for('main.index'))
