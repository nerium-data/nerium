# -*- coding: utf-8 -*-
from marshmallow import Schema, fields
from nerium.app import api


@api.schema("Default")
class ResultSchema(Schema):
    name = fields.Str(attribute='name')
    data = fields.List(fields.Dict(), attribute='result')
    metadata = fields.Dict()
    params = fields.Dict()
    error = fields.Str()
