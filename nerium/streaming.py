import abc

from io import StringIO

BUFFER_SIZE = 16384


def initialize_stream(iterable, writer_constructor):
    """Initialize a stream and writer. Popping the first record from
    the iterable allows both for error handling prior to entering a
    stream generator as well as header formatting. The first record will
    be written to the `stream` buffer here.

    Args:
        `iterable`: an iterable of results, e.g. a generator streaming
            a sqlalchemy cursor
        `writer_constructor`: a class or callable whose return
            implements the BufferWriter interface

    Returns:
        A tuple containing, respectively, a stream (StringIO stream
        buffer) and a writer (implementing BufferWriter). These can be
        passed to yield_stream along with the original `iterable` to
        yield the stream until completion

    """

    stream = StringIO()

    try:
        first = next(iterable)
    except StopIteration:
        return stream, None

    writer = writer_constructor(stream, first)
    writer.write(first)

    return stream, writer


def yield_stream(iterable, stream, writer):
    """Buffers contents of iterable to stream and yields blocks of
    BUFFER_SIZE until completion. Arguments `stream` and `writer` are
    expected to be the return values of `initialize_stream`.

    Args:
        `iterable`: an iterable of results, e.g. a generator streaming
            a sqlalchemy cursor
        `stream`: an iterable of results, e.g. a generator streaming
            a sqlalchemy cursor
        `writer`: serializes each record in the iterable to the
            StringIO buffer. Implements the BufferWriter interface.

    Yields:
        bytes: serialized records form iterable

    """

    for row in iterable:
        writer.write(row)
        if stream.tell() > BUFFER_SIZE:
            yield _flush(stream)
    yield _flush(stream)


def _flush(stream):
    """Consume the current StringIO buffer and return the contents"""

    stream.seek(0)
    data = stream.read()
    stream.truncate(0)
    stream.seek(0)

    return data


class BufferWriter(metaclass=abc.ABCMeta):
    """Interface specifying serialization to a StringIO buffer"""

    @abc.abstractmethod
    def __init__(self, stream, first_record):
        pass

    @abc.abstractmethod
    def write(self, record):
        pass
