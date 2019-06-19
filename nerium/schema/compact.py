# -*- coding: utf-8 -*-
from marshmallow import Schema, fields


class ResultSchema(Schema):
    columns = fields.Function(lambda obj: list(obj.result[0].keys()))
    data = fields.Function(lambda obj: [tuple(row.values()) for row in obj.result])
