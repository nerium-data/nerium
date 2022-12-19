from csv import DictWriter

from nerium.query import serialize_stream
from nerium.streaming import BufferWriter


class CsvStreamWriter(BufferWriter):
    """Serializes dicts to a StringIO buffer"""

    def __init__(self, stream, first_record):
        self.stream = stream
        self.writer = DictWriter(stream, fieldnames=first_record.keys())
        self.writer.writeheader()

    def write(self, record):
        """Absraction to support writers with methods other than writerow"""

        self.writer.writerow(record)


def results_to_csv(query_name, **kwargs):
    """Generate CSV from result data"""

    return serialize_stream(query_name, CsvStreamWriter, **kwargs)
