#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from conf.settings import PORT, HOST, DEBUG
from util import json_response

import business

app = Flask(__name__)


@app.route('/')
@json_response
def index():
    return map(str, app.url_map.iter_rules())

app.register_blueprint(business.app, url_prefix="/business")

if __name__ == '__main__':
    app.debug = DEBUG
    app.run(host=HOST, port=PORT)
