#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path

import yaml
from munch import munchify


# Load Nerium config file
def config():
    DEFAULTS = {
        'query_extensions': {
            'sql': 'SQLResultSet'
        },
        'formats': {
            'default': 'DefaultFormatter'
        },
        'databases': [{
            'default':
            os.getenv('DATABASE_URL', 'sqlite:///')
        }]
    }
    configfile = os.getenv('CONFIG_PATH', Path.cwd() / 'nerium-config.yaml')
    try:
        with open(configfile, 'r') as cfgfile:
            usr_cfg = yaml.load(cfgfile)
    except FileNotFoundError:
        usr_cfg = {}
    cfg = {**DEFAULTS, **usr_cfg} 
    return munchify(cfg)


config = config()

# yapf: disable
from nerium.main import *  # noqa F401
# yapf: enable
