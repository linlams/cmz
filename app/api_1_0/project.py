from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Project, Department
from ..util import json_response
from . import api
from .errors import forbidden


@api.route('/project/<int:id>')
def get_project(id):
    entity = Project.query.get_or_404(id)
    return jsonify(entity.to_json())


@api.route('/department/<int:id>/project')
@json_response
def get_department_projects(id):
    entity = Department.query.get_or_404(id)
    return [mc.to_json() for mc in entity.projects]
