# -*- coding: utf-8 -*-
"""
Duplicator is used as a duplication strategy for datasets.

It will take a series of rows of the dataset, duplicate and append them.
You can also add random noise to the duplicated rows.
"""
from datafuzz.dataset import DataSet
from datafuzz.strategy import Strategy
from datafuzz.utils.noise_helpers import messy_spaces, generate_random_int, \
    generate_random_float


class Duplicator(Strategy):
    """ Duplicator is used to duplicate rows in a dataset

        see also: `strategy.Strategy`
    """

    def __init__(self, dataset, **kwargs):
        """
        see `strategy.Stragegy init`

        Additional Kwargs:
            add_noise (bool): add noise to duplicated rows
        """
        super().__init__(dataset, **kwargs)
        self.add_noise = kwargs.get('add_noise')

    def run_strategy(self):
        """
        Run duplicator strategy and if add noise is selected,
        add noise to the data before appending it to the dataset.
        """
        sample = self.dataset.sample(self.percentage)

        if self.add_noise:
            sample = self.noise(sample)

        self.dataset.append(sample)

    def noise(self, sample):
        """ Adds noise to the duplicate rows

            Parameteres:
                sample (list or obj): `dataset.Dataset.sample`

            Returns
                sample (list or obj): distorted rows

            TODO:
                - implement more noise options than just random

        """
        sample_dataset = DataSet(sample.copy())
        columns = sample_dataset.sample(self.percentage, columns=True)
        if sample_dataset.data_type == 'pandas':
            sample_dataset.records = \
                sample_dataset.records.reset_index(drop=True)

        for column in columns:
            col = sample_dataset.column_idx(column)
            col_type = sample_dataset.column_dtype(col)
            func = None

            if 'float' in str(col_type):
                func = generate_random_float
            elif 'int' in str(col_type):
                func = generate_random_int
            if func:
                kwargs = {'low': self.dataset.column_agg(col, min),
                          'high': self.dataset.column_agg(col, max)}
                if kwargs.get('low') == kwargs.get('high'):
                    kwargs['high'] += 1

                sample = self.apply_func_to_column(
                    lambda x: func(x, **kwargs), col)
            elif col_type in [object, str]:
                sample = self.apply_func_to_column(messy_spaces, col,
                                                   dataset=sample_dataset)
        return sample_dataset.records
