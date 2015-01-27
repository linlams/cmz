#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import yaml
import logging
import logging.config


def setup_logging(
    default_path='conf/logging.yml',
    default_level=logging.INFO,
    env_key='LOG_CFG',
):
    """Setup logging configuration"""
    path = default_path

    value = os.getenv(env_key, None)
    if value:
        path = value

    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

setup_logging()
