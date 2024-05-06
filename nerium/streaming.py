import abc

BUFFER_SIZE = 16384


def initialize_stream(iterable, writer_constructor, **kwargs):
    """Initialize a BufferWriter. Popping the first record from
    the iterable allows both for error handling prior to entering a
    stream generator as well as header formatting. The first record will
    be written with the `writer` here.

    Args:
        `iterable`: an iterable of results, e.g. a generator streaming
            a sqlalchemy cursor
        `writer_constructor`: a class or callable whose return
            implements the BufferWriter interface

    Returns:
        A writer (implementing BufferWriter). This can be passed to
        `yield_stream` along with the original `iterable` to yield the stream
        until completion.

    """

    try:
        first = next(iterable)
    except StopIteration:
        return NullBufferWriter()

    writer = writer_constructor(first)
    writer.write(first)

    return writer


def yield_stream(iterable, writer, **kwargs):
    """Buffers contents of iterable to writer/stream and yields blocks of
    BUFFER_SIZE until completion. Argument `writer` is expected to be the
    return values of `initialize_stream`.

    Args:
        `iterable`: an iterable of results, e.g. a generator streaming
            a sqlalchemy cursor
        `writer`: serializes each record in the iterable to the
            StringIO buffer. Implements the BufferWriter interface.

    Yields:
        bytes: serialized records form iterable

    """

    for row in iterable:
        writer.write(row)
        if writer.target_stream_size() > BUFFER_SIZE:
            # ensure all data is written to the stream from GzipFile
            writer.flush()
            yield writer.consume_target_stream()

    # the compressed writer/stream must be closed/flushed before we can read
    # the last bit of data from the target stream
    writer.close()
    yield writer.consume_target_stream()


class BufferWriter(metaclass=abc.ABCMeta):
    """Interface specifying serialization to an IOBase buffer"""

    @abc.abstractmethod
    def __init__(self, first_record):
        pass

    @property
    @abc.abstractmethod
    def target_stream(self):
        pass

    @target_stream.setter
    @abc.abstractmethod
    def target_stream(self, stream):
        pass

    @abc.abstractmethod
    def write(self, record):
        pass

    @abc.abstractmethod
    def consume_target_stream(self):
        pass

    @abc.abstractmethod
    def target_stream_size(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def flush(self):
        pass


class BufferWriterBase(BufferWriter):
    """Base class for BufferWriter implementations"""

    def __init__(self, stream):
        self._target_stream = stream

    @property
    def target_stream(self):
        return self._target_stream

    @target_stream.setter
    def target_stream(self, stream):
        self._target_stream = stream

    def write(self, record):
        raise NotImplementedError

    def consume_target_stream(self):
        """Consume the target_stream buffer and return the contents"""

        if not self.target_stream.closed:
            self.target_stream.seek(0)
        data = self.target_stream.read()
        if not self.target_stream.closed:
            # BytesIO requires seek(0) before truncate(0)
            self.target_stream.seek(0)
            self.target_stream.truncate(0)
            self.target_stream.seek(0)

        return data

    def target_stream_size(self):
        return self.target_stream.tell()

    def close(self):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError


class NullBufferWriter(BufferWriterBase):
    def __init__(self):
        super().__init__(None)

    def write(self, data):
        pass

    def consume_target_stream(self):
        return ""

    def target_stream_size(self):
        return 0

    def close(self):
        pass

    def flush(self):
        pass
