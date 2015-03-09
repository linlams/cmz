# -*- coding: utf-8 -*-
from flask import render_template, redirect, request, url_for
from flask.ext.login import current_user
import urllib2
import json
from config import KSSO_LOCAL_URL, KSSO_SERVER_URL
from . import handler
from ..models import Vhost, Host, Memcached

@handler.route('/deploy_mc/<mc_id>')
def deploy_mc(mc_id):
    mc = Memcached.query.get(int(mc_id))
    import pdb; pdb.set_trace()
    return str(mc)


@handler.route('/logout')
def logout():
    logout_user()
    return redirect('/')
    #return redirect(request.args.get('next') or url_for('main.index'))
