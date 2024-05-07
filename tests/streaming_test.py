import pytest

from nerium import streaming
from io import StringIO, BytesIO


class Writer(streaming.BufferWriterBase):

    def __init__(self, _first):
        super().__init__(StringIO())

    def write(self, record):
        self._target_stream.write(f"<{record}>")

    def close(self):
        pass

    def flush(self):
        pass


class BytesWriter(streaming.BufferWriterBase):

    def __init__(self, _first):
        super().__init__(BytesIO())

    def write(self, record):
        self._target_stream.write(record)

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
    max_record = 9000  # chosen > BUFFER_SIZE
    return (i.to_bytes(2, 'big') for i in range(max_record))


def test_initialize_stream(results):
    writer = streaming.initialize_stream(results, Writer, format_="csv")
    assert writer.target_stream_size() == 3
    assert writer.consume_target_stream() == "<0>"
    assert next(results) == 1


def test_initialize_stream_compressed(byte_results):
    writer = streaming.initialize_stream(byte_results, BytesWriter, format_="csv.gz")
    assert writer.target_stream_size() == 2
    assert writer.consume_target_stream() == b'\x00\x00'
    assert next(byte_results) == b'\x00\x01'


def test_initialize_stream_empty_iterator():
    writer = streaming.initialize_stream(iter(()), None)
    assert writer.target_stream_size() == 0
    assert writer.consume_target_stream() == ""


def test_yield_stream(results):
    writer = streaming.initialize_stream(results, Writer)
    blocks = list(streaming.yield_stream(results, writer))
    assert "<0><1><2><3>" in blocks[0]
    assert "<2914><2915>" in blocks[0]
    assert "<2916><2917>" in blocks[1]
    assert writer.consume_target_stream() == ""


def test_yield_stream_bytes(byte_results):
    writer = streaming.initialize_stream(byte_results, BytesWriter)
    blocks = list(streaming.yield_stream(byte_results, writer))
    assert b'\x00\x01\x00\x02' in blocks[0] # beginning of block
    assert b'\x1f\xff\x20\x00' in blocks[0] # end of block
    assert b'\x20\x01\x20\x02' in blocks[1] # beginning of block
    assert b'\x23\x26\x23\x27' in blocks[1] # end of block
    assert writer.consume_target_stream() == b''
