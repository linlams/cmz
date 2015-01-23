#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request
from conf.settings import PORT, HOST, DEBUG
from handler import supervisor_rpc_api

app = Flask(__name__)


