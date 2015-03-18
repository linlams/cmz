# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, redirect, session
from . import memcached
from .forms import MemcachedForm
from .. import db
from ..models import User, Role, Department, Memcached, Project, Vhost, Host, Idc, Keepalived
from ..handler.supervisor_rpc_api import SupervisorController
from ..handler.myansible import ansible_save, ansible_file, ansible_yum, add_vip, remove_vip
from ..util import json_response
from flask.ext.login import login_required


def start(id):
    mc = Memcached.query.get(id)
    process_name = u'{project_name}_memcached_{vip}_{vport}'.format(
            project_name=mc.project.name,
            vip=mc.vhost.ip,
            vport=mc.vhost_port,
        )
    sc = SupervisorController(mc.host.ip)

    results = add_vip([mc.host.ip], mc.vhost.ip)

    deploy(id)
    result = sc.update([process_name])
    result = sc.start([process_name])
    if result[0]['statename'] == 'RUNNING':
        mc.status = 1
    return result[0]


@memcached.route('/start/<int:id>', methods=['GET', 'POST'])
@json_response
def _start(id):
    return start(id)


@memcached.route('/status/<int:id>', methods=['GET'])
@json_response
def status(id):
    mc = Memcached.query.get(id)
    process_name = u'{project_name}_memcached_{vip}_{vport}'.format(
            project_name=mc.project.name,
            vip=mc.vhost.ip,
            vport=mc.vhost_port,
        )
    sc = SupervisorController(mc.host.ip)

    result = sc.status([process_name])
    if result[0]['statename'] == 'RUNNING':
        import pdb; pdb.set_trace()
        mc.status = 1
    return result[0]

def stop(id):
    mc = Memcached.query.get(id)
    process_name = u'{project_name}_memcached_{vip}_{vport}'.format(
            project_name=mc.project.name,
            vip=mc.vhost.ip,
            vport=mc.vhost_port,
        )
    sc = SupervisorController(mc.host.ip)
    result = sc.update([process_name])
    result = sc.stop([process_name])

    if Memcached.query.filter_by(vhost=mc.vhost).count() == 1:
        results = remove_vip([mc.host.ip], mc.vhost.ip)

    undeploy(id)
    if len(result) == 0 or result[0]['statename'] == 'STOPPED':
        mc.status = 0
    return result


@memcached.route('/stop/<int:id>', methods=['GET', 'POST'])
@json_response
def _stop(id):
    return stop(id)


def deploy(id):
    mc = Memcached.query.get(id)
    ansible_yum([mc.host.ip], 'memcached', 'installed'),

    process_name = u'{project_name}_memcached_{vip}_{vport}'.format(
            project_name=mc.project.name,
            vip=mc.vhost.ip,
            vport=mc.vhost_port,
        )
    from jinja2 import Environment, PackageLoader
    env = Environment(loader=PackageLoader('app', 'templates'))
    template = env.get_template('/etc/supervisord/conf.d/memcached.conf.template')
    content = template.render(**mc.__dict__)
    result = ansible_save([mc.host.ip], content, '/etc/supervisord/conf.d/%s.conf' % process_name)
    if result['contacted']:
        mc.deployed = True
    return result


@memcached.route('/deploy/<int:id>', methods=['GET', 'POST'])
@json_response
def _deploy(id):
    return deploy(id)


def undeploy(id):
    mc = Memcached.query.get(id)
    process_name = u'{project_name}_memcached_{vip}_{vport}'.format(
            project_name=mc.project.name,
            vip=mc.vhost.ip,
            vport=mc.vhost_port,
        )
    result = ansible_file([mc.host.ip], '/etc/supervisord/conf.d/%s.conf' % process_name, state='absent')
    if result['contacted']:
        mc.deployed = False
    return result


@memcached.route('/undeploy/<int:id>', methods=['GET', 'POST'])
@json_response
def _undeploy(id):
    return undeploy(id)


@memcached.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # import pdb; pdb.set_trace()
    form = MemcachedForm()
    form.idc_id.choices = [(str(x.id), x.en_name) for x in Idc.query.all()]
    form.project_id.choices = [(str(x.id), x.en_name) for x in Project.query.all()]
    form.vhost_id.choices = [(str(x.id), x.ip) for x in Vhost.query.all()]
    form.host_id.choices = [(str(x.id), x.ip) for x in Host.query.all()]
    form.keepalived_id.choices = [(str(x.id), x.name) for x in Keepalived.query.all()]
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            mc_id = form.id.data
            mc = Memcached.query.get(mc_id)
            # undeploy(mc_id)
            # stop(mc_id)
        else:
            mc = Memcached()

        mc.project = Project.query.get(form.project_id.data)
        mc.keepalived = Keepalived.query.get(form.keepalived_id.data)
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
        return redirect(url_for('memcached.index'))

    memcacheds = Memcached.query.all()
    return render_template('model/memcached.html',
                           memcacheds=memcacheds,
                           form=form,)


@memcached.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    undeploy(id)
    stop(id)
    db.session.delete(Memcached.query.get(id))
    return redirect(url_for('memcached.index'))
