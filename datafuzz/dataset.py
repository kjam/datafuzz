# -*- coding: utf-8 -*-
"""
Datasets are a class used to hold imported data and newly generated data.

All transformations require a dataset, which will be manipulated by
the library and eventually exported for use.
"""
import collections
import os
import random
import re
from json import load
from csv import DictReader
import dataset as dataset_db
from datafuzz.settings import HAS_PANDAS, HAS_NUMPY

from datafuzz.output.helpers import obj_to_output

if HAS_PANDAS:
    import pandas as pd

if HAS_NUMPY:
    import numpy as np


class DataSet(object):
    """
    DataSet objects are used as the primary datatype for \
    passing around data in datafuzz.

    If pandas is installed, it will use dataframes to load \
    and transform data; otherwise, it will use a list. \
    You can also specify to not use pandas by passing \
    keyword argument `pandas=False`.

    Supported inputs are JSON and CSV files, numpy 2D arrays, \
    sql queries (you must pass a `db_uri` keyword argument and \
    a `query` argument), pandas DataFrames and Python lists \
    (of dictionaries or lists).

    Attributes:
        DATA_TYPES (str):   list of possible datatypes (pandas, numpy, list).
        FILE_REGEX (str):   regex to find file name
        USE_PANDAS(bool):   boolean that determines whether pandas is
                            installed and also OK to use (no `pandas=False`)
        records   (list):   data records for
        input      (obj):   initial input for dataset
                        (can be dataframe, list, numpy array, filename or `sql`)
        output     (str):   output
                           (if specified, can be dataframe, list,
                                                numpy array, filename or `sql`)
        original   (obj):   copy of input which won't be modified
        data_type  (str):   dataset datatype (pandas, numpy, list).
        db_uri     (str):   dataset database connection string
                            (required only if using `sql` as input or output)
        query      (str):   dataset database select query string
                            (required only if using `sql` as input)
        table      (str):   dataset database output table
                            (required only if using `sql` as output)

    """
    USE_PANDAS = HAS_PANDAS
    USE_NUMPY = HAS_NUMPY
    DATA_TYPES = ['pandas', 'numpy', 'list']
    FILE_REGEX = r'file://(?P<filename>.*)'

    def __init__(self, input_obj, **kwargs):
        self.records = []
        self.input = input_obj
        self.original = input_obj
        self.data_type = None
        self.output = kwargs.get('output')
        self.db_uri = None
        self.table = None
        self.query = None
        self.index = -1
        validate_db = False

        if kwargs.get('pandas') is False:
            self.USE_PANDAS = False
        if isinstance(self.input, str) and self.input == 'sql':
            self.db_uri = kwargs.get('db_uri')
            self.query = kwargs.get('query')
            validate_db = True
        if isinstance(self.output, str) and self.output == 'sql':
            if not self.db_uri:
                self.db_uri = kwargs.get('db_uri')
            self.table = kwargs.get('table')
            validate_db = True

        if validate_db:
            self.validate_db()

        self._parse_input()
        self.validate_parsed()

    def __len__(self):
        """ Return length of self.records """
        if self.data_type in ['pandas', 'numpy']:
            return self.records.shape[0]
        return len(self.records)

    def __iter__(self):
        """ Iterator object of self.records """
        return self

    def __next__(self):
        """ Iterator object of self.records This uses `self.index`.

            NOTE: index is only reset on init.

            TODO:
                - find best way to reset index to -1 on next loop

        """
        self.index = self.index + 1
        if self.index >= len(self):
            raise StopIteration
        if self.data_type == 'pandas':
            return self.records.iloc[self.index, :]
        elif self.data_type == 'numpy':
            return self.records[self.index, :]
        return self.records[self.index]

    def __getitem__(self, idx):
        """ Return rows from self.records based on index """
        if self.data_type == 'pandas':
            return self.records.iloc[idx, :]
        elif self.data_type == 'numpy':
            return self.records[idx, :]
        return self.records[idx]

    def _parse_input(self):
        """ initialization method which will call read input
            for the passed input type (in init). This will use \
            the _read_$type methods to then generate the \
            `self.input`, `self.data_type`, `self.records` \
            and `self.original` attributes.

            NOTE: Files are parsed using regex and searching \
            for file://$file_name
        """
        if self.USE_PANDAS and isinstance(self.input, pd.DataFrame):
            self._read_pandas()
        elif self.USE_NUMPY and isinstance(self.input, np.ndarray):
            self._read_numpy()
        elif isinstance(self.input, str):
            if self.input.startswith('file:'):
                if self.input.endswith('.csv'):
                    self._read_csv()
                elif self.input.endswith('.json'):
                    self._read_json()
            elif self.input == 'sql':
                self._read_sql()
        elif isinstance(self.input, list):
            self._read_list()

    def validate_parsed(self):
        """ Validate if data was properly parsed. This tests:

                - valid data types
                - records properly parsed and set to self.records
                - self.original exists

            It will raise an exception if the validation fails.
        """
        try:
            assert self.original is not None
            assert self.data_type in self.DATA_TYPES
            assert not isinstance(self.records, str)
            assert isinstance(self.records, collections.Iterable)
        except AssertionError:
            raise TypeError('Unsupported input: {}'.format(self.input))
        try:
            assert len(self.records) > 0
        except AssertionError:
            raise Exception('Could not parse data for: {}'.format(self.input))

    def validate_db(self):
        """ Validate that proper variables are set and a connection \
            can be established with the database if either \
            input or output are set to `sql`.

            This will raise an exception if validation fails.
        """
        try:
            assert self.db_uri is not None
            assert self.query is not None or self.table is not None
            assert dataset_db.connect(self.db_uri)
        except AssertionError:
            raise Exception(
                'You must define a valid db_uri and ' +
                'query or table to use SQL.')

    def _read_pandas(self):
        """ Read in pandas dataframe"""
        self.original = self.input
        self.data_type = 'pandas'
        self.records = self.original.copy()

    def _read_numpy(self):
        """ Read in numpy array"""
        self.original = self.input
        self.data_type = 'numpy'
        self.records = self.input.copy()

    def _read_csv(self):
        """ Read in csv to list or dataframe"""
        self.original = self.input
        if self.USE_PANDAS:
            with open(self.input_filename, 'r') as myf:
                self.input = pd.read_csv(myf)
            self.data_type = 'pandas'
        else:
            with open(self.input_filename, 'r') as myf:
                self.input = list(DictReader(myf))
            self.data_type = 'list'
        self.records = self.input.copy()

    def _read_sql(self):
        """ Read in sql to list or dataframe"""
        self.original = self.input
        if self.USE_PANDAS:
            self.input = pd.read_sql_query(self.query, self.db_uri)
            self.data_type = 'pandas'
        else:
            with dataset_db.connect(self.db_uri) as db:
                self.input = list(db.query(self.query))
            self.data_type = 'list'
        self.records = self.input.copy()

    def _read_json(self):
        """ Read in json to list or dataframe"""
        self.original = self.input
        if self.USE_PANDAS:
            with open(self.input_filename, 'r') as myf:
                self.input = pd.read_json(myf)
            self.data_type = 'pandas'
        else:
            with open(self.input_filename, 'r') as myf:
                self.input = load(myf)
            self.data_type = 'list'
            if not isinstance(self.input, list):
                raise Exception(
                    'The JSON file must contain a list for datafuzz use.')
        self.records = self.input.copy()

    def _read_list(self):
        """ Read in list to list or dataframe"""
        self.original = self.input
        if self.USE_PANDAS:
            self.input = pd.DataFrame(self.input)
            self.data_type = 'pandas'
        else:
            self.data_type = 'list'
        self.records = self.input.copy()

    @property
    def input_filename(self):
        """ Return filename if input follows proper file format \
            file://[absolute or relative filepath]

            NOTE: this will raise an exception if the file is not found
        """
        filename = re.match(self.FILE_REGEX, self.original).group('filename')
        if not os.path.exists(filename):
            raise Exception('Could not retrieve filename {}'.format(filename))
        return filename

    @property
    def output_filename(self):
        """ Return filename if output follows proper file format \
            file://[absolute or relative filepath]
        """
        return re.match(self.FILE_REGEX, self.output).group('filename')

    def sample(self, percentage, columns=False):
        """ Get a sample from the dataset.

            Arguments:
                percentage (float): percentage of dataset to sample \
                                    should be a value from 0.0-1.0

            Kwargs:
                columns     (bool): option to sample columns from dataset \
                                    default is False
            Returns:
                A sample from the dataset with matching datatype
        """
        if self.data_type == 'pandas':
            if columns:
                sample = np.random.choice(
                    self.records.columns,
                    round(self.records.shape[1] * percentage), replace=False)
            else:
                sample = self.records.sample(frac=percentage)
        elif self.data_type == 'numpy':
            if columns:
                sample = np.random.choice(
                    range(len(self.records[0])),
                    round(len(self.records[0]) * percentage), replace=False)
            else:
                sample = self.records[
                    np.random.choice(self.records.shape[0],
                                     round(self.records.shape[0] * percentage),
                                     replace=False)]
        else:
            if columns:
                sample = random.sample(
                    range(len(self.records[0])),
                    round(len(self.records[0]) * percentage))

            else:
                sample = random.sample(self.records,
                                       round(len(self.records) * percentage))
        return sample

    def append(self, rows):
        """ Append rows to DataSet records

            Arguments:
                rows (list): rows to add or concatenate

            TODO:
                - is a shuffle needed?
                - should the index be maintained or reordered
                - should new indexes be ordered or not
        """
        if self.data_type == 'list':
            self.records.extend(rows)
        elif self.data_type == 'numpy':
            self.records = np.append(self.records, rows, axis=0)
        else:
            if not isinstance(rows, pd.DataFrame):
                rows = pd.DataFrame(rows)
            self.records = self.records.append(rows, ignore_index=True)

    def to_output(self):
        """ Transform DataSet records to output. \
            This uses helper method `obj_to_output` \
            located in `output/helpers.py`

            Returns output object or filepath.
        """
        return obj_to_output(self)

    def column_idx(self, column):
        """ Return numeric index of a column

            NOTE: if column is not found, raises an AttributeError
        """
        if isinstance(column, str) and column.isnumeric():
            return int(column)
        elif self.data_type == 'pandas':
            return self.records.columns.get_loc(column)
        elif self.data_type == 'list' and isinstance(self.records[0], dict):
            return list(self.records[0].keys()).index(column)
        elif isinstance(column, int):
            return column
        elif not isinstance(column, str):
            if HAS_NUMPY and np.issubdtype(column, np.integer):
                return column
        raise AttributeError('Column {} could not be found!'.format(column))

    def column_dtype(self, column):
        """ Return dtype of column

            Arguments:
                column (int): column index

            Return:
                data type of the column

            TODO:
                - determine smart way to test more than one row for a list?
        """
        if self.data_type == 'pandas':
            return self.records.iloc[:, column].dtype
        elif self.data_type == 'numpy':
            return self.records[:, column].dtype
        elif isinstance(self.records[0], dict):
            return type(list(self.records[0].values())[column])
        return type(self.records[0][column])

    def column_agg(self, column, agg_func):
        """ Perform aggregate function on given column

            Arguments:
               column        (int): column index
               agg_func (function): aggregate function to perform on column

            Returns aggregate result

            Example:

                `dataset.column_agg(3, min)`
        """
        if self.data_type == 'pandas':
            return agg_func(self.records.iloc[:, column])
        elif self.data_type == 'numpy':
            return agg_func(self.records[:, column])
        elif isinstance(self.records[0], dict):
            return agg_func([list(x.values())[column] for x in self.records])
        return agg_func([x[column] for x in self.records])
