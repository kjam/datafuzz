# -*- coding: utf-8 -*-
"""
Helpers for output generation.
"""
from datafuzz.settings import HAS_PANDAS, HAS_NUMPY
from datafuzz.output.core import CSVOutput, JSONOutput, SQLOutput

if HAS_PANDAS:
    import pandas as pd

if HAS_NUMPY:
    import numpy as np


def obj_to_output(obj):
    """ Transform DataSet or generator records to output

        supported outputs:
            dataset, pandas, numpy, list, csv and json
            (specify file://$NAME.csv or file://$NAME.json)
            and sql (specify db_uri and table)

        NOTE: will raise exception if unsupported output set
    """
    if obj.output is None or obj.data_type == obj.output:
        return obj.records
    elif obj.output == 'dataset':
        from datafuzz import DataSet
        return DataSet(obj.records)
    elif obj.output == 'pandas' and HAS_PANDAS:
        return pd.DataFrame(obj.records)
    elif obj.output == 'numpy' and HAS_NUMPY:
        if obj.data_type == 'pandas':
            return obj.records.values
        return np.array(obj.records)
    elif obj.output == 'list':
        if obj.data_type == 'numpy':
            return obj.records.tolist()
        elif obj.data_type == 'pandas':
            return list(obj.records.T.to_dict().values())
    elif obj.output.startswith('file://'):
        if obj.output.endswith('.csv'):
            output = CSVOutput(obj, filename=obj.output_filename)
            return output.to_csv()

        elif obj.output.endswith('.json'):
            output = JSONOutput(obj, filename=obj.output_filename)
            return output.to_json()
        else:
            raise NotImplementedError(
                'Only CSV and JSON file types supported.')
    elif obj.output == 'sql':
        output = SQLOutput(obj, db_uri=obj.db_uri, table=obj.table)
        return output.to_sql()
    raise NotImplementedError(
        'Output {} not supported'.format(obj.output))
