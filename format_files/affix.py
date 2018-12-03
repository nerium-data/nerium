# -*- coding: utf-8 -*-
"""Wrap default object array with error and metadata details
"""
from marshmallow import Schema, fields


class ResultSchema(Schema):
    error = fields.Str()
    response = fields.List(fields.Dict(), attribute='result')
    metadata = fields.Dict()
    params = fields.Dict()
    executed = fields.Str()
