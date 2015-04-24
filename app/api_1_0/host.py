from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Host
from . import api
from .errors import forbidden


@api.route('/host/<int:id>')
def get_host(id):
    entity = Host.query.get_or_404(id)
    return jsonify(entity.to_json())
