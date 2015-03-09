# -*- coding: utf-8 -*-
from flask import Blueprint

mc = Blueprint('mc', __name__)

from . import views
