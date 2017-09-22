# -*- coding: utf-8 -*-
"""
Output classes for transforming datasets into proper output.

Supported output: CSV, JSON, SQL, pandas, np 2D array, lists
"""
import json
from csv import DictWriter, writer
import dataset as dataset_db

from datafuzz.settings import HAS_NUMPY

if HAS_NUMPY:
    import numpy as np


class BaseOutput:
    """ Base class for output.

        Arguments:
            dataset (`datafuzz.DataSet` or
            `generators.DatasetGenerator`): dataset or generator to output

        Attributes:
            records     (obj): DataSet or generator records obj / list
            data_type   (str): DataSet or generator data_type string
            output      (str): DataSet or generator output string

        Keyword Arguments:
            filename    (str): DataSet or generator output string
    """

    def __init__(self, dataset, **kwargs):
        self.records = dataset.records
        self.data_type = dataset.data_type
        self.output = dataset.output
        if 'filename' in kwargs:
            self.output = kwargs.get('filename')


class CSVOutput(BaseOutput):
    """ CSV output for writing datasets to CSV file.

        see also: `datafuzz.output.BaseOutput`
    """

    def to_csv(self):
        """ Write the CSVOutput to a csv file """
        if self.data_type == 'pandas':
            self.records.to_csv(self.output)
        elif self.data_type == 'numpy':
            np.savetxt(self.output, self.records, delimiter=",")
        elif isinstance(self.records[0], dict):
            with open(self.output, 'w') as output:
                wrtr = DictWriter(output, fieldnames=self.records[0].keys())
                wrtr.writeheader()
                wrtr.writerows(self.records)
        else:
            with open(self.output, 'w') as output:
                wrtr = writer(output)
                wrtr.writerows(self.records)
        return self.output


class JSONOutput(BaseOutput):
    """ JSON output for writing datasets to JSON file.

        see also: `datafuzz.output.BaseOutput`
    """

    def to_json(self):
        """ Write the JSONOutput to a json file """
        if self.data_type == 'pandas':
            self.records.T.to_json(self.output)
        elif self.data_type == 'numpy':
            json.dump(self.records.to_list(),
                      open(self.output, 'w', encoding='utf-8'),
                      indent=4)
        else:
            json.dump(self.records,
                      open(self.output, 'w', encoding='utf-8'),
                      indent=4)
        return self.output


class SQLOutput(BaseOutput):
    """ Database output for writing datasets to a table.

        see also: `datafuzz.output.BaseOutput`

        Extra parameters:
            db_uri (str): Database URI String
            table  (str): Database table name
    """
    def __init__(self, dataset, **kwargs):
        super().__init__(dataset, **kwargs)
        self.db_uri = kwargs.get('db_uri')
        self.table = kwargs.get('table')

    def to_sql(self):
        """ Write the dataset records to a sql table """
        if self.data_type == 'pandas':
            return self.records.to_sql(self.table, self.db_uri)
        with dataset_db.connect(self.db_uri) as db:
            table = db[self.table]
            return table.insert_many(self.records)
