# -*- coding: utf-8 -*-
"""
Strategies define how the data will be fuzzed, duplicated, noised and altered.
"""
import logging
from datafuzz.utils.noise_helpers import numpy_type_transform
from datafuzz.settings import HAS_NUMPY

if HAS_NUMPY:
    import numpy as np


class Strategy(object):
    """ Strategy objects apply predefined noise and fuzz to datasets.

        Parameters:
            dataset (`datafuzz.DataSet`): dataset to noise / alter

        Kwargs:
            percentage  (int)           : percentage to distort (0-100)
                                          If none given, default to 30

        Attributes:
            dataset (`datafuzz.DataSet`): dataset to noise / alter
            percentage (float)          : percentage to distort (0-1)


        NOTE: each strategy type may have additional required keyword arguments

        see also: `duplicator.Duplicator`, `noise.NoiseMaker` and `fuzz.Fuzzer`
    """

    def __init__(self, dataset, **kwargs):
        self.dataset = dataset
        self.type = kwargs.get('type')
        if kwargs.get('percentage'):
            self.percentage = kwargs.get('percentage') / 100
        else:
            self.percentage = .3

        try:
            assert 0 < self.percentage < 1
        except AssertionError:
            raise Exception('You must define a percentage between 1 and 100')

    @property
    def num_rows(self):
        """ return number of rows to transform in dataset
            based on given percentage.

            NOTE: this uses rounding so only whole numbers are returned.
        """
        if self.dataset.data_type in ['pandas', 'numpy']:
            return round(
                self.dataset.records.shape[0] * self.percentage)
        return round(len(self.dataset.records) * self.percentage)

    def get_numeric_columns(self, columns):
        """ Ensure columns are numeric, this will get indexes
            of string column names (i.e. Pandas columns or dict keys)

            Arguments:
                columns (list of str or int): column list

            Returns:
                columns        (list of int): column list (only ints)
        """
        if all([isinstance(c, int) or
                (isinstance(c, str) and c.isnumeric()) for c in columns]):
            columns = [int(c) for c in columns]
        if self.dataset.data_type == 'pandas' and any([isinstance(c, str)
                                                       for c in columns]):
            columns = [self.dataset.column_idx(col) for col in columns]
        return columns

    def apply_func_to_column(self, function, column, dataset=None):
        """
        Apply a function to a column in a given dataset.

        (this should work as uniformly as possible across data types)

        Arguments:
            function    (lambda or other func): function to apply
            column                       (int): column index

        Kwargs:
            dataset        (`dataset.DataSet`): dataset to use
                                                defaults to self.dataset

        Returns:
            None

        Note: This performs transformations on `dataset.records` in place.
        """
        if dataset is None:
            dataset = self.dataset
        if dataset.data_type in ['pandas', 'numpy']:
            indexes = list(np.random.choice(dataset.records.shape[0],
                                            self.num_rows))
            if self.dataset.data_type == 'pandas':
                self.dataset.records.iloc[indexes, column] = \
                        dataset.records.iloc[indexes, column].map(function)
            else:
                try:
                    dataset.records[indexes, column] = np.apply_along_axis(
                        function, 0, dataset.records[indexes, column])
                except (TypeError, ValueError):
                    try:
                        func = np.vectorize(function)
                        dataset.records[indexes, column] = np.apply_along_axis(
                            func, 0, dataset.records[indexes, column])
                    except ValueError as exc:
                        # Force type change.
                        try:
                            numpy_type_transform(exc, dataset)
                            dataset.records[indexes,
                                            column] = np.apply_along_axis(
                                                function, 0,
                                                dataset.records[indexes,
                                                                column])
                        except ValueError:
                            logging.exception('Could not transform numpy type')
        else:
            indexes = np.random.choice(
                len(dataset.records), self.num_rows)
            dataset.records = [
                val if idx not in indexes else
                [v if i != column else function(v) for i, v in enumerate(val)]
                for idx, val in enumerate(dataset.records)]
        return dataset
