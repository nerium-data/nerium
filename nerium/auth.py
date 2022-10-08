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
        # If API_KEY is set in environment, require valid key sent in header
        if API_KEY:
            api_key = request.headers.get("X-API-Key")
            # 400 error if required header is not set
            if not api_key:
                return {"error": "Missing API key"}, 400
            # Check if API key is correct and valid, 403 if not
            elif api_key == API_KEY:
                return func(*args, **kwargs)
            else:
                return {"error": "The provided API key is not valid"}, 403
        # If no API_KEY, just pass through
        else:
            return func(*args, **kwargs)

    return decorator
