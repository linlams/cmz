# -*- coding: utf-8 -*-
from flask import Blueprint

memcached = Blueprint('memcached', __name__)

from . import views
