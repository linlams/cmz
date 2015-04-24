from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import User
from . import api
from .errors import forbidden

@api.route('/admin/')
def get_admin():
    admin_role = Role.query.filter_by(code='admin').first()
    admin = User.query.filter_by(role=admin_role).first_or_404()
    return jsonify(admin.to_json())
