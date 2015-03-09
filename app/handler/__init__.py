# -*- coding: utf-8 -*-
from flask import Blueprint

handler = Blueprint('handler', __name__)

from . import views
