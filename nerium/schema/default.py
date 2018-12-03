# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, pre_dump


class ResultSchema(Schema):
    name = fields.Str(attribute='name')
    data = fields.List(fields.Dict(), attribute='result')
    metadata = fields.Dict()
    params = fields.Dict()

    @pre_dump
    def unwrap_metadata(self, obj):
        obj.metadata = dict(obj.metadata)
        return obj
