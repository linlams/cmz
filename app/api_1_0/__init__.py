from flask import Blueprint

api = Blueprint('api', __name__)

from . import memcached, admin, errors, authentication, keepalived, vhost, host, project, department
