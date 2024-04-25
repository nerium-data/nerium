import abc

from io import StringIO, BytesIO

BUFFER_SIZE = 16384


def initialize_stream(iterable, writer_constructor, **kwargs):
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

    stream = BytesIO() if kwargs.get("format_") == "csv.gz" else StringIO()

    try:
        first = next(iterable)
    except StopIteration:
        return stream, None

    writer = writer_constructor(stream, first)
    writer.write(first)

    return stream, writer


def yield_stream(iterable, stream, writer, **kwargs):
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
            # ensure all data is written to the stream from GzipFile
            writer.flush()
            yield _consume(stream)

    # the compressed writer/stream must be closed/flushed before we can read
    # the last bit of data from the target stream
    writer.close()
    yield _consume(stream)


def _consume(stream):
    """Consume the current StringIO/BytesIO buffer and return the contents"""

    if not stream.closed:
        stream.seek(0)
    data = stream.read()
    if not stream.closed:
        # BytesIO requires seek(0) before truncate(0)
        stream.seek(0)
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

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def flush(self):
        pass
