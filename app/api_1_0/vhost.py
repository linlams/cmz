from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Vhost
from . import api
from .errors import forbidden


@api.route('/vhost/<int:id>')
def get_vhost(id):
    entity = Vhost.query.get_or_404(id)
    return jsonify(entity.to_json())
