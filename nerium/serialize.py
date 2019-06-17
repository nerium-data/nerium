from datetime import datetime
from decimal import Decimal
from functools import singledispatch


@singledispatch
def serialize(obj):
    return str(obj)


@serialize.register(datetime)
def serial_datetime(obj):
    return obj.isoformat() + "Z"


@serialize.register(Decimal)
def serial_decimal(obj):
    return float(obj)


@serialize.register(float)
@serialize.register(int)
def serial_number(obj):
    return obj
