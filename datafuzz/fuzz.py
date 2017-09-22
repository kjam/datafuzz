# -*- coding: utf-8 -*-
"""
Fuzzer adds basic "dumb" fuzzing strategies to datafuzz.

It will apply a random set of noise and fuzz based on the
column type (or sometimes randomly).
"""
import random
from datafuzz.strategy import Strategy
from datafuzz.utils.fuzz_helpers import add_format, change_encoding, \
        to_bytes, insert_boms, nanify, bigints, hexify,  \
        sql, metachars, files, delimiter, emoji


class Fuzzer(Strategy):
    """ Fuzzer is used as a strategy to add "dumb" fuzzing methods
        (i.e. random bad values). These transformations
        are mainly based on column type.

        see also: `strategy.Strategy`

    """

    def __init__(self, dataset, **kwargs):
        """ See `strategy.Strategy`

            Additional kwargs:
                columns    (list of str): list of indexes or column names
                                          If not columns are given, a random
                                          set will be chosen.

        """
        self.columns = kwargs.get('columns')
        super().__init__(dataset, **kwargs)
        if not self.columns:
            self.columns = self.dataset.sample(self.percentage,
                                               columns=True)
        self.columns = self.get_numeric_columns(self.columns)

    def run_strategy(self):
        """ Apply fuzz methods to chosen columns.

            For now, this applies a mixture of random
            and column type based transformations.

            See `Fuzzer.fuzz_str`, `Fuzzer.fuzz_random`
            and `Fuzzer.fuzz_numeric` for full list of
            possible transformations.
        """
        for column in self.columns:
            col_type = self.dataset.column_dtype(column)
            if random.randint(0, 100) < 20:
                fuzz = self.fuzz_random()
            elif col_type in [object, str]:
                fuzz = self.fuzz_str()
            elif 'int' or 'float' in str(col_type):
                fuzz = self.fuzz_numeric()

            self.apply_func_to_column(fuzz, column)

    def fuzz_str(self):
        """ Return random choice from string
            fuzz helpers.


            Possible transformations:
                - add_format:      insert format strings
                - change_encoding: decode with possibly bad encoding
                - to_bytes:        transform to bytes
                - insert_boms:     insert utf-8 boms
        """
        return random.choice([add_format, change_encoding,
                              to_bytes, insert_boms])

    def fuzz_numeric(self):
        """ Return a random choice from the numeric
            fuzz helpers.

            Possible transformations:
                - nanify:     insert null values (sometimes strs)
                - bigints:    return big magic numbers
                - hexify:     return hex value
        """
        return random.choice([nanify, bigints, hexify])

    def fuzz_random(self):
        """ Return a random choice from the random
            fuzz helpers.

            Possible transformations:
                - sql:        returns unkind sql
                - metachars:  inserts metacharacters
                - files:      returns filepaths or bash
                - delimiter:  inserts multiple delimiters
                - emoji:      inserts one random emoji
        """
        return random.choice([sql, metachars, files, delimiter, emoji])
