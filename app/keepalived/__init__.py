# -*- coding: utf-8 -*-
from flask import Blueprint

keepalived = Blueprint('keepalived', __name__)

from . import views
