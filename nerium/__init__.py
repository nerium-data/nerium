#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path

import yaml
from munch import munchify


from nerium.version import __version__  # noqa F401


# Load Nerium config file
def config():
    DEFAULTS = {
        'data_sources': [{
            'name': 'default',
            'url': "os.getenv('DATABASE_URL', 'sqlite:///')"
        }]
    }
    configfile = os.getenv('CONFIG_PATH', Path.cwd() / 'nerium-config.yaml')
    try:
        with open(configfile, 'r') as cfgfile:
            usr_cfg = yaml.safe_load(cfgfile)
    except FileNotFoundError:
        usr_cfg = {}
    cfg = {**DEFAULTS, **usr_cfg}
    return munchify(cfg)


config = config()

# yapf: disable
# from nerium.lib import *  # noqa F401
# yapf: enable
