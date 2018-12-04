#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nerium.commit import get_commit_for_version
from nerium.version import __version__  # noqa F401

commit = get_commit_for_version(__version__)
