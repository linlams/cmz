# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, redirect, jsonify
from . import keepalived
from .forms import KeepalivedForm
from .. import db
from ..models import User, Role, Department, Keepalived, Project, Vhost, Host, Idc
from ..handler.supervisor_rpc_api import SupervisorController
from ..handler.myansible import ansible_save, ansible_file
from ..util import json_response


def start(id):
    mc = Keepalived.query.get(id)
    process_name = u'{project_name}_keepalived_{vip}_{vport}'.format(
            project_name=mc.project.name,
            vip=mc.vhost.ip,
            vport=mc.vhost_port,
        )
    sc = SupervisorController(mc.host.ip)
    deploy(id)
    result = sc.update([process_name])
    result = sc.start([process_name])
    if result[0]['statename'] == 'RUNNING':
        mc.status = 1
    return result[0]


@keepalived.route('/start/<int:id>', methods=['GET', 'POST'])
@json_response
def _start(id):
    return start(id)


def stop(id):
    mc = Keepalived.query.get(id)
    process_name = u'{project_name}_keepalived_{vip}_{vport}'.format(
            project_name=mc.project.name,
            vip=mc.vhost.ip,
            vport=mc.vhost_port,
        )
    sc = SupervisorController(mc.host.ip)
    result = sc.update([process_name])
    result = sc.stop([process_name])
    undeploy(id)
    if result[0]['statename'] == 'STOPPED':
        mc.status = 0
    return result


@keepalived.route('/stop/<int:id>', methods=['GET', 'POST'])
@json_response
def _stop(id):
    return stop(id)


def deploy(id):
    mc = Keepalived.query.get(id)
    process_name = u'{project_name}_keepalived_{vip}_{vport}'.format(
            project_name=mc.project.name,
            vip=mc.vhost.ip,
            vport=mc.vhost_port,
        )
    from jinja2 import Environment, PackageLoader
    env = Environment(loader=PackageLoader('app', 'templates'))
    template = env.get_template('/etc/supervisord/conf.d/keepalived.conf.template')
    content = template.render(**mc.__dict__)
    result = ansible_save([mc.host.ip], content, '/etc/supervisord/conf.d/%s.conf' % process_name)
    if result['contacted']:
        mc.deployed = True
    return result


@keepalived.route('/deploy/<int:id>', methods=['GET', 'POST'])
@json_response
def _deploy(id):
    return deploy(id)


def undeploy(id):
    mc = Keepalived.query.get(id)
    process_name = u'{project_name}_keepalived_{vip}_{vport}'.format(
            project_name=mc.project.name,
            vip=mc.vhost.ip,
            vport=mc.vhost_port,
        )
    result = ansible_file([mc.host.ip], '/etc/supervisord/conf.d/%s.conf' % process_name, state='absent')
    if result['contacted']:
        mc.deployed = False
    return result


@keepalived.route('/undeploy/<int:id>', methods=['GET', 'POST'])
@json_response
def _undeploy(id):
    return undeploy(id)


@keepalived.route('/', methods=['GET', 'POST'])
def index():
    form = KeepalivedForm()
    form.idc_id.choices = [(str(x.id), x.name) for x in Idc.query.all()]
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            mc_id = form.id.data
            mc = Keepalived.query.get(mc_id)
            undeploy(mc_id)
            stop(mc_id)
        else:
            mc = Keepalived()

        mc.project = Project.query.get(form.project_id.data)
        mc.vhost = Vhost.query.get(form.vhost_id.data)
        mc.host = Host.query.get(form.host_id.data)
        mc.vhost_port = form.vhost_port.data
        mc.host_port = form.host_port.data
        mc.max_mem_size = form.max_mem_size.data

        db.session.add(mc)
        if form.id.data:
            flash(u'修改成功!')
        else:
            flash(u'保存成功!')
        return redirect(url_for('keepalived.index'))

    keepaliveds = Keepalived.query.all()
    return render_template('model/keepalived.html',
                           keepaliveds=keepaliveds,
                           form=form,)


@keepalived.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    undeploy(id)
    stop(id)
    db.session.delete(Keepalived.query.get(id))
    return redirect(url_for('keepalived.index'))
