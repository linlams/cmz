# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, redirect, jsonify
from . import keepalived
from .forms import KeepalivedForm
from .. import db
from ..models import User, Role, Department, Keepalived, Project, Vhost, Host, Idc
from ..handler.supervisor_rpc_api import SupervisorController
from ..handler.myansible import ansible_save, ansible_service, ansible_file
from ..util import json_response


def start(id):
    k = Keepalived.query.get(id)
    master_ip = k.ip
    backup_ip = k.backup_ip

    vips = list(set(map(lambda x: x.vhost.ip, k.memcacheds)))

    master = {
        'ip': master_ip,
        'host_interface': k.host_interface,
        'memcacheds': k.memcacheds,
        'master': True,
        'priority': 100,
        'vips': vips,
    }
    master_status = deploy(master)
    backup = {
        'ip': backup_ip,
        'host_interface': k.backup_host_interface,
        'memcacheds': k.memcacheds,
        'master': False,
        'priority': 99,
        'vips': vips,
    }
    backup_status = deploy(backup)
    
    if master_status and backup_status:
        k.deployed=True

    result = ansible_service([master_ip, backup_ip], 'keepalived', 'started') 
    if result['contacted']:
        k.status = 1
    return result

@keepalived.route('/start/<int:id>', methods=['GET', 'POST'])
@json_response
def _start(id):
    '启动 Keepalived'
    return start(id)


def stop(id):
    k = Keepalived.query.get(id)
    master_ip, backup_ip = k.ip, k.backup_ip
    result = ansible_service([master_ip, backup_ip], 'keepalived', 'stopped') 
    if result['contacted']:
        k.status = 0
    return result


@keepalived.route('/stop/<int:id>', methods=['GET', 'POST'])
@json_response
def _stop(id):
    '关闭 Keepalived'
    return stop(id)


def deploy(keepalived):
    from jinja2 import Environment, PackageLoader
    env = Environment(loader=PackageLoader('app', 'templates'))
    template = env.get_template('/etc/keepalived/keepalived.conf.template')
    content = template.render(**keepalived)
    result = ansible_save([keepalived['ip']], content, '/etc/keepalived/keepalived.conf')
    if result['contacted']:
        return True
    return False


@keepalived.route('/', methods=['GET'])
def index():
    form = KeepalivedForm()
    form.idc_id.choices = [(str(x.id), x.code) for x in Idc.query.all()]
    form.csrf_enabled = True

    keepaliveds = Keepalived.query.all()
    return render_template('model/keepalived.html',
                           keepaliveds=keepaliveds,
                           form=form,)


@keepalived.route('/', methods=['POST'])
def save():
    '保存keepalived信息'
    form = KeepalivedForm()
    form.idc_id.choices = [(str(x.id), x.code) for x in Idc.query.all()]
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            mc_id = form.id.data
            k = Keepalived.query.get(mc_id)
            # stop(mc_id)
        else:
            k = Keepalived()

        k = form.fill_model(k)

        db.session.add(k)
        if form.id.data:
            flash(u'修改成功!')
        else:
            flash(u'保存成功!')
        return redirect(url_for('keepalived.index'))

    keepaliveds = Keepalived.query.all()
    return render_template('model/keepalived.html',
                           keepaliveds=keepaliveds,
                           form=form,)


def undeploy(keepalived):
    k = Keepalived.query.get(id)
    result1 = ansible_file([k.ip], '/etc/keepalived/keepalived.conf', 'absent')
    result2 = ansible_file([k.backup_ip], '/etc/keepalived/keepalived.conf', 'absent')

    if result1['contacted'] and result2['contacted']:
        return True
    return False


@keepalived.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    '删除keepalived信息'
    undeploy(id)
    stop(id)
    db.session.delete(Keepalived.query.get(id))
    return redirect(url_for('keepalived.index'))
