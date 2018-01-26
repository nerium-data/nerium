import os

import records
from dotenv import find_dotenv, load_dotenv

# Provision environment as needed
if find_dotenv():
    load_dotenv(find_dotenv())
else:
    load_dotenv('/dotenv/.env')


class RecordsQueryable():

    def results(self, query_file, **kwargs):
        backend_code = self.parse(query_file)
        try:
            backend = records.Database(self.backend_lookup(backend_code))
            results = backend.query_file(query_file, **kwargs)
            result_dict = results.as_dict()
        except Exception as e:
            result_dict = [{'error': repr(e)}]
        return result_dict

    def parse(self, file_path):
        parts = file_path.split('/')
        end = parts[-1]
        file_parts = end.split('.')
        return ''.join(file_parts[1:])

    def backend_lookup(self, backend_code):
        try:
            backend = os.getenv('{}_BACKEND'.format(backend_code.upper()))
        except Exception:
            backend = os.getenv('DATABASE_URL', "NO BACKEND")
        return backend
