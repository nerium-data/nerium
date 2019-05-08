import re
from pathlib import Path
# from types import SimpleNamespace

from nerium import query


def result(query, **kwargs):
    data_path = Path(query.metadata["source_file"])
    with open(data_path) as file_:
        data = file_.readlines()
    match_pattern = re.compile(query.body)
    matched_data = [row.strip() for row in data if re.search(match_pattern, row)]
    return matched_data


if __name__ == "__main__":
    query = query.parse_query_file('mock.grep')
    r = result(query)
    for i in r:
        print(i)
