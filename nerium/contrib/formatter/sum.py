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

    def is_float(self, maybefloat):
        if isinstance(maybefloat, float):
            return True
        else:
            try:
                float(maybefloat)
                return True
            except:
                return False

    def format_results(self):
        raw = self.result
        formatted = {}
        formatted['error'] = False
        formatted['response'] = {}
        formatted['response']['summary'] = {}
        formatted['metadata'] = {}
        formatted['metadata']['executed'] = datetime.datetime.now().isoformat()
        formatted['metadata']['params'] = self.kwargs
        if not 'grouping' in raw[0].keys():
            formatted['response']['result'] = raw
            return formatted
        raw_data, groupings = self.transform_grouping_sets(raw)
        formatted['response']['result'] = raw_data
        #figure out what the groupings relate to by looking at what columns are and aren't supplied with it.
        for dictionary in groupings:
            value_set = []
            for key, value in dictionary.items():
                if value != None and isinstance(value, str) and not self.is_float(value):
                    value_set.append(value)
            if value_set == []:
                value_set = 'overall_total'
            else:
                value_set = '_'.join(value_set)
            formatted['response']['summary'][value_set] = {key: val for key, val in dictionary.items() if val != None}
        return formatted