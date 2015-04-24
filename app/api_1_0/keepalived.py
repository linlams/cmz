from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Keepalived
from . import api
from .errors import forbidden


@api.route('/keepalived/<int:id>')
def get_keepalived(id):
    entity = Keepalived.query.get_or_404(id)
    return jsonify(entity.to_json())
