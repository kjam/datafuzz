# -*- coding: utf-8 -*-
"""
NoiseMaker adds noise strategies to datafuzz.

This will apply specified noise transformations to a series
of columns.
"""
import logging
import random
from datafuzz.settings import HAS_NUMPY
from datafuzz.strategy import Strategy
from datafuzz.utils.noise_helpers import messy_spaces, generate_random_int, \
    generate_random_float

if HAS_NUMPY:
    import numpy as np


class NoiseMaker(Strategy):
    """ NoiseMaker applies noisy data transformations
        to given dataset.

        see also `strategy.Strategy`

    """


    def __init__(self, dataset, **kwargs):
        """ See `strategy.Strategy`

            Additional kwargs:
                noise      (list of str): list of noise options to apply

                columns    (list of str): list of indexes or column names
                                          If not columns are given, a random
                                          set will be chosen.
                limits  (list of limits): range limits (list of ints)

            Available noise options:
                'add_nulls': add null values
                'string_permutation': apply string transformations
                'random': generate some random values based on col type
                'range': change values into given or column range
                'type_transform': apply type transformations
        """
        super().__init__(dataset, **kwargs)
        self.columns = kwargs.get('columns')
        self.limits = kwargs.get('limits')
        try:
            assert isinstance(kwargs.get('noise'), list)
            self.noise = kwargs.get('noise')
            assert self.noise
        except AssertionError:
            raise Exception('You must specify what types of noise to apply.')

        if not self.columns:
            self.columns = self.dataset.sample(self.percentage, columns=True)
        self.columns = self.get_numeric_columns(self.columns)

    def run_strategy(self):
        """ Run noise strategy on sample

            Performs transformations on self.dataset
        """
        if 'add_nulls' in self.noise:
            self.nullify()
        if 'string_permutation' in self.noise:
            self.string_permutation()
        if 'random' in self.noise:
            self.randomize()
        if 'range' in self.noise:
            self.use_range()
        if 'type_transform' in self.noise:
            self.type_transform()

    def set_value(self, value, column=None):
        """ Set value for a series of columns or one column.

            Arguments:
                value         (obj): value to set

            Kwargs:
                column (str or int): name or index of column

            TODO:
                - should this be available on Strategy class?
        """
        if column is None:
            for col in self.columns:
                self.set_value(value, column=col)
        if self.dataset.data_type == 'pandas':
            self.dataset.records.ix[
                np.random.choice(
                    self.dataset.records.shape[0],
                    self.num_rows), column] = value
        elif self.dataset.data_type == 'numpy':
            self.dataset.records[
                np.random.choice(
                    self.dataset.records.shape[0],
                    self.num_rows), column] = value
        else:
            indexes = np.random.choice(len(self.dataset.records),
                                       self.num_rows)
            self.dataset.records = [
                val if idx not in indexes else
                [v if i != column else value for i, v in enumerate(val)]
                for idx, val in enumerate(self.dataset.records)]

    def nullify(self):
        """ Set null values for sample in columns """
        for column in self.columns:
            self.set_value(np.nan, column=column)

    def randomize(self):
        """ Set random values for sample in columns

            NOTE: this will vary based on column type
        """
        for column in self.columns:
            col_type = self.dataset.column_dtype(column)
            min_val = self.dataset.column_agg(column, min)
            max_val = self.dataset.column_agg(column, max)

            func = None

            if 'float' in str(col_type):
                func = generate_random_float
            elif 'int' in str(col_type):
                func = generate_random_int
            if func:
                self.apply_func_to_column(
                    lambda x: func(min_val, max_val), column)
            elif col_type in [object, str]:
                self.string_permutation(column=column)

    def string_permutation(self, column=None):
        """ Permute string values for sample in columns

            TODO:
                - add permutations for missing characters
                - flipped strings
                - typos
                - homonyms / autocorrect
        """
        if column is None:
            for col in self.columns:
                self.string_permutation(column=col)
        else:
            self.apply_func_to_column(messy_spaces, column)

    def use_range(self):
        """ Use values from a range to set values in columns

            If `limits` not passed during initialization, this
            method will attempt to determine good limits based
            on the column ranges and use those.

            NOTE: range is only available for numeric columns

            TODO:
                - should we calculate IQR and insert outliers?
                - if not, should add_outliers be a new option for noise?
        """
        for column in self.columns:
            if self.limits is None:
                min_val = self.dataset.column_agg(column, min)
                max_val = self.dataset.column_agg(column, max)
            else:
                min_val = self.limits[0]
                max_val = self.limits[1]

            func = None
            col_type = self.dataset.column_dtype(column)
            if 'float' in str(col_type):
                func = generate_random_float
            elif 'int' in str(col_type):
                func = generate_random_int
            if func:
                self.apply_func_to_column(lambda x: func(x,
                                                         low=min_val,
                                                         high=max_val),
                                          column)
            elif col_type in [object, str]:
                raise NotImplementedError(
                    'You must use a numeric column when using `range`')

    def type_transform(self):
        """ Transform types for sample in columns.

            NOTE: if a string column is used and the values cannot
            be transformed into integer or float values, you
            may not see a useful transformation.

            TODO:
                - for strings, should numeric values be inserted as strings
                instead?

        """
        for column in self.columns:
            col_type = self.dataset.column_dtype(column)
            if 'int' in str(col_type):
                func = lambda x: random.choice([str, float])(x)
            elif 'float' in str(col_type):
                func = lambda x: random.choice([str, int])(x)
            elif col_type in [object, str]:
                func = lambda x: random.choice([float, int])(x)
            if func:
                try:
                    self.apply_func_to_column(func, column)
                except (ValueError, TypeError):
                    logging.exception(
                        'Could not change type for column: %s', column)
