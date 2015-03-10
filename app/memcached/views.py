# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, redirect, jsonify
from . import memcached
from .. import db
from ..models import User, Role, Department, Memcached, Project, Vhost, Host, Idc
from ..handler.supervisor_rpc_api import SupervisorController
from ..handler.myansible import ansible_save
from ..util import json_response


def start(id):
    mc = Memcached.query.get(id)
    process_name = u'{project_name}_memcached_{vip}_{vport}'.format(
            project_name=mc.project.name,
            vip=mc.vhost.ip,
            vport=mc.vhost_port,
        )
    sc = SupervisorController(mc.host.ip)
    result = sc.start([process_name])
    if result[0]['statename'] == 'RUNNING':
        mc.status = 1
        db.session.add(mc)
    return result[0]


@memcached.route('/start/<int:id>', methods=['GET', 'POST'])
@json_response
def _start(id):
    return start(id)


def stop(id):
    mc = Memcached.query.get(id)
    process_name = u'{project_name}_memcached_{vip}_{vport}'.format(
            project_name=mc.project.name,
            vip=mc.vhost.ip,
            vport=mc.vhost_port,
        )
    sc = SupervisorController(mc.host.ip)
    result = sc.stop([process_name])
    if result[0]['statename'] == 'STOPPED':
        mc.status = 0
        db.session.add(mc)
    return result


@memcached.route('/stop/<int:id>', methods=['GET', 'POST'])
@json_response
def _stop(id):
    return stop(id)


def deploy(id):
    mc = Memcached.query.get(id)
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
    return result


@memcached.route('/deploy/<int:id>', methods=['GET', 'POST'])
@json_response
def _deploy(id):
    return deploy(id)
