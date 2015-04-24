#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: 王旭林
# Mail: wangxulin108@gmail.com

from os import listdir
from os.path import isfile, join
import json

SUPERVISOR_CONF_D = '/etc/supervisord/conf.d/'

filenames = filter(lambda fn: isfile(join(SUPERVISOR_CONF_D, fn)) and fn.endswith('.conf'), listdir(SUPERVISOR_CONF_D))
def get_memcached_info(info):
    project_code, vip_and_port_str = info.split('_memcached_')
    vhost, port = vip_and_port_str[:-5].split('_')
    return {
        'project_code': project_code,
        'vhost': vhost,
        'port': int(port),
    }

memcached_infos = map(get_memcached_info, filenames)

def format_for_discovery(d):
    return dict(map(lambda x: ('{#%s}' % x[0].upper(), x[1]), d.iteritems()))

print json.dumps({'data': map(format_for_discovery, memcached_infos)})
