from csv import DictWriter
from gzip import GzipFile
from io import TextIOWrapper

from nerium.query import serialize_stream
from nerium.streaming import BufferWriterBase


class GzipCompressWriteStream(BufferWriterBase):
    def __init__(self, stream):
        super().__init__(stream)
        self.binary_file = GzipFile(fileobj=stream, mode='wb')
        encoding = 'utf-8'

        self.text_io = TextIOWrapper(
                self.binary_file,
                encoding,
                write_through=True,
                line_buffering=False,
                errors='strict')

    def write(self, data):
        self.text_io.write(data)

    def close(self):
        self.binary_file.close()

    def flush(self):
        self.text_io.flush()
        self.binary_file.flush()


class CsvStreamWriter(BufferWriterBase):
    """Serializes dicts to a StringIO buffer"""

    def __init__(self, stream, first_record):
        super().__init__(stream)
        self.writer = DictWriter(stream, fieldnames=first_record.keys())
        self.writer.writeheader()

    def write(self, record):
        """Absraction to support writers with methods other than writerow"""

        self.writer.writerow(record)

    def close(self):
        pass

    def flush(self):
        pass


class CsvGzipStreamWriter(BufferWriterBase):
    """Serializes dicts to a compressed StringIO buffer"""

    def __init__(self, stream, first_record):
        super().__init__(stream)
        self.gzip_stream = GzipCompressWriteStream(stream)

        self.writer = DictWriter(self.gzip_stream, fieldnames=first_record.keys())
        self.writer.writeheader()

    def write(self, record):
        """Absraction to support writers with methods other than writerow"""

        self.writer.writerow(record)

    def close(self):
        self.gzip_stream.close()

    def flush(self):
        self.gzip_stream.flush()


def results_to_csv(query_name, **kwargs):
    """Generate CSV from result data"""

    writer = CsvGzipStreamWriter if kwargs.get("format_") == "csv.gz" else CsvStreamWriter

    return serialize_stream(query_name, writer, **kwargs)
