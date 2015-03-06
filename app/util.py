#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import jinja2
import json
import functools
from collections import defaultdict, Iterator
from bson import json_util
import hashlib
from flask import Response
import urllib
import urllib2

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
import time


def md5(*args):
    length = len(args)
    if length == 0:
        return None

    str = None
    if length == 1:
        str = args[0]
    else:
        str = '_'.join(args)

    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()


def json_response(func):
    '把函数的返回值以json的格式输出'
    @functools.wraps(func)
    def _(*args, **kwargs):
        begin = time.time()
        res = func(*args, **kwargs)
        end = time.time()

        if (end - begin) > 0.01:
            current_app.logger.warning('Slow request: %s\n\tMethod: %s\n \tDuration: %s\n' %
                                       (request.url, request.method, end - begin))

        status = 200
        if isinstance(res, tuple):
            if len(res) == 2:
                res, status = res
            elif len(res) == 3:
                res, status, headers = res
        json_str = to_json(res) if not isinstance(res, basestring) else res
        return Response(json_str, mimetype='application/json', status=status)
    return _


def to_json(o):
    o = list(o) if isinstance(o, Iterator) else o
    return json.dumps(o, default=json_util.default, separators=(',', ':'))


def get_tags_in_levels(pure_namespaces):
    'pure_namespaces'
    tags_in_levels = defaultdict(list)
    for pure_namespace in pure_namespaces:
        for k, v in pure_namespace.iteritems():
            if v not in tags_in_levels[k]:
                tags_in_levels[k].append(v)
    return tags_in_levels


def remove_duplicate(iterable, key=None):
    '以key作为唯一标识，去除序列中的重复元素'
    iter_dict = dict(map(lambda x: (key(x), x), iterable))
    return iter_dict.values()


def to_boolean(s):
    return s in {'True', 'true', 'on', '1', 'yes'}


def to_integer(s):
    return int(s)


def to_float(s):
    return float(s)


def to_number(s):
    return to_float(s)

TYPE_CONVERTORS = dict(
    boolean=to_boolean,
    integer=to_integer,
    float=to_float,
    number=to_number,
)

# TODO: cerberus types
#    string
#    integer
#    float
#    number (integer or float)
#    boolean
#    datetime
#    dict (formally collections.mapping)
#    list (formally collections.sequence, exluding strings)
#    set


CONVERTORS = {
    'json': json.loads,
}


def __urllib_method__(url, data, method='GET', result_format='json', headers=None):
    'urllib2, urllib'
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    req = urllib2.Request(url, urllib.urlencode(data))
    req.get_method = lambda: method
    fd = opener.open(req)
    result = fd.read()
    if result_format in CONVERTORS:
        return CONVERTORS[result_format](result)
    else:
        return result


def get_json(url, headers=None):
    return __urllib_method__(url, None, 'GET', 'json', headers)


def post_json(url, data, headers=None):
    return __urllib_method__(url, data, 'POST', 'json', headers)


def put_json(url, data, headers=None):
    return __urllib_method__(url, data, 'PUT', 'json', headers)


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__name__), 'templates')))

TEMPLATE_DICT = {
    'memcached': '/etc/supervisord/conf.d/memcached.conf.template',
    'memcached.filename': '/etc/supervisord/conf.d/memcached.conf.filename',
    'keepalived': '/etc/keepalived/keepalived.conf',
}


def conf_file_template(conf_file_type):
    conf_file_template = env.get_template(TEMPLATE_DICT[conf_file_type])

    print conf_file_template

    def _(**kwargs):
        return conf_file_template.render(kwargs)
    return _
