#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path

import yaml
from munch import munchify

from nerium.commit import get_commit_for_version
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
commit = get_commit_for_version(__version__)
