#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
   Settings
'''
import pymongo
import redis
import logging_settings
import logging

REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

SUPERVISOR_RPC_URL_TEMPLATE = 'http://{username}:{password}@{host}:9001/RPC2'
SUPERVISOR_RPC_KWARGS = {
    'username': '',
    'password': '',
    'host': 'localhost',
}

CACHE_EXPIRE_TIME = 3600
CACHE = redis.StrictRedis(host=REDIS['host'], port=REDIS['port'], db=REDIS['db'])


MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DBNAME = 'memcached_mgr'
MONGO_STATE_DBNAME = 'memcached_mgr_state'

KSSO = dict(
    USERNAME='',
    PASSWORD='',
)


HOST = "0.0.0.0"
PORT = 9999

DEBUG = False

SUPERVISOR_CONFS_DIR = '/etc/supervisord/conf.d'

try:
    from local_settings import *
except ImportError:
    pass

__mclient__ = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)

db = __mclient__[MONGO_DBNAME]

state_db = __mclient__[MONGO_STATE_DBNAME]
logger = logging.getLogger(__name__)
logger.error(state_db)
