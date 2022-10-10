#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import os

from flask import request


def require_api_key(func):
    """Decorator that requires a request to have a valid X-API-Key header
    if API_KEY is set in the environment
    """

    @functools.wraps(func)
    def decorator(*args, **kwargs):
        API_KEY = os.getenv("API_KEY")
        # If API_KEY is not provided in environment, just pass through
        if not API_KEY:
            return func(*args, **kwargs)

        # Otherwise API_KEY is set. Require valid key sent in header:
        api_key = request.headers.get("X-API-Key")
        # 400 error if required header is not set
        if not api_key:
            return {"error": "Missing API key"}, 400
        # Check if API key is correct and valid, 403 if not
        elif api_key == API_KEY:
            return func(*args, **kwargs)
        else:
            return {"error": "The provided API key is not valid"}, 403

    return decorator
