import pytest

from nerium import streaming


class Writer(streaming.BufferWriter):
    def __init__(self, stream, _first):
        self.stream = stream

    def write(self, record):
        self.stream.write(f"<{record}>")

    def close(self):
        pass

    def flush(self):
        pass


class BytesWriter(streaming.BufferWriter):

    def __init__(self, stream, _first):
        self.stream = stream

    def write(self, record):
        self.stream.write(record)

    def close(self):
        pass

    def flush(self):
        pass


@pytest.fixture
def results():
    max_record = 2918  # chosen from BUFFER_SIZE and serialization length
    return (i for i in range(max_record))


@pytest.fixture
def byte_results():
    max_record = 2918  # chosen from BUFFER_SIZE and serialization length
    return (i.to_bytes(2, 'big') for i in range(max_record))


def test_initialize_stream(results):
    stream, writer = streaming.initialize_stream(results, Writer, format_="csv")
    assert stream.getvalue() == "<0>"
    assert next(results) == 1


def test_initialize_stream_compressed(byte_results):
    stream, writer = streaming.initialize_stream(byte_results, BytesWriter, format_="csv.gz")
    assert stream.getvalue() == b'\x00\x00'
    assert next(byte_results) == b'\x00\x01'


def test_initialize_stream_empty_iterator():
    stream, writer = streaming.initialize_stream(iter(()), None)
    assert stream.getvalue() == ""


def test_yield_stream(results):
    stream, writer = streaming.initialize_stream(results, Writer)
    blocks = list(streaming.yield_stream(results, stream, writer))
    assert "<0><1><2><3>" in blocks[0]
    assert "<2914><2915>" in blocks[0]
    assert "<2916><2917>" in blocks[1]
    assert stream.getvalue() == ""
