import pytest

from nerium import streaming

class Writer(streaming.BufferWriter):
    def __init__(self, stream, _first):
        self.stream = stream

    def write(self, record):
        self.stream.write(f"<{record}>")


@pytest.fixture
def results():
    max_record = 2918  # chosen from BUFFER_SIZE + serialization length
    return (i for i in range(max_record))


def test_initialize_stream(results):
    stream, writer = streaming.initialize_stream(results, Writer)
    assert stream.getvalue() == '<0>'
    assert next(results) == 1


def test_initialize_stream_empty_iterator():
    stream, writer = streaming.initialize_stream(iter(()), None)
    assert stream.getvalue() == ''


def test_yield_stream(results):
    stream, writer = streaming.initialize_stream(results, Writer)
    blocks = list(streaming.yield_stream(results, stream, writer))
    assert '<0><1><2><3>' in blocks[0]
    assert '<2914><2915>' in blocks[0]
    assert '<2916><2917>' in blocks[1]
    assert stream.getvalue() == ''
