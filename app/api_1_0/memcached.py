from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Memcached, Host, Vhost, Project
from . import api
from .errors import forbidden

@api.route('/memcached/<host_type>/<ip>/port/<int:port>')
def get_memcached_by_host_ip_and_host_port(host_type, ip, port):
    host_classes = {
        'host': Host,
        'vhost': Vhost,
    }
    if host_type not in host_classes:
        abort(400, 'host_type error')
    host = host_classes[host_type].query.filter_by(ip=ip).first_or_404()

    mc = Memcached.query.filter_by(host=host, host_port=port).first_or_404()
    return jsonify(mc.to_json())

@api.route('/memcached/<int:id>')
def get_memcached(id):
    mc = Memcached.query.get_or_404(id)
    return jsonify(mc.to_json())

@api.route('/project/<int:id>/memcached')
def get_project_memcacheds(id):
    entity = Project.query.get_or_404(id)
    return jsonify([mc.to_json() for mc in entity.memcacheds])
