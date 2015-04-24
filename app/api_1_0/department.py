from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Department
from . import api
from .errors import forbidden


@api.route('/department/<int:id>')
def get_department(id):
    entity = Department.query.get_or_404(id)
    return jsonify(entity.to_json())
