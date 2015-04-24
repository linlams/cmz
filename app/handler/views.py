# -*- coding: utf-8 -*-
from flask import render_template, redirect, request, url_for
from flask.ext.login import current_user
import urllib2
import json
from config import KSSO_LOCAL_URL, KSSO_SERVER_URL
from . import handler
from .supervisor_rpc_api import SupervisorController
from ..models import Vhost, Host, Memcached
