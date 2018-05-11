import datetime

from nerium import ResultFormatter


class SumFormatter(ResultFormatter):

    def transform_grouping_sets(self, result):
        raw_data = []
        groupings = []
        for row in result:
            output_row = {key: val for key, val in row.items() if key != 'grouping'}
            if row['grouping'] == 0:
                raw_data.append(output_row)
            elif row['grouping'] > 0:
                groupings.append(output_row)
        return (raw_data, groupings)

    def format_results(self):
        raw = self.result
        formatted = {}
        formatted['error'] = False
        formatted['response'] = {}
        formatted['response']['summary'] = []
        formatted['metadata'] = {}
        formatted['metadata']['executed'] = datetime.datetime.now().isoformat()
        formatted['metadata']['params'] = self.kwargs
        if not 'grouping' in raw[0].keys():
            formatted['response']['result'] = raw
            return formatted
        raw_data, groupings = self.transform_grouping_sets(raw)
        formatted['response']['result'] = raw_data
        formatted['response']['summary'] = groupings
        return formatted
