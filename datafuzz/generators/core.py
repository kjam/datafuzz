# -*- coding: utf-8 -*-
"""
Generators are used to produce datasets to use with datafuzz.

You must have faker installed to use the generator.
"""
import collections
import logging
import random
import re
from datetime import timedelta
from faker import Faker

from datafuzz.settings import HAS_NUMPY
from datafuzz.output import obj_to_output

if HAS_NUMPY:
    from numpy import arange


class AttributeDict(dict):
    """ Use a dictionary like an object with attributes instead of keys.

        See: https://stackoverflow.com/a/5021467
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class DatasetGenerator(object):
    """ DatasetGenerator creates a dataset when given a parsed YAML
        or series of CLI arguments or passed arguments.

        Attributes:
            parser  (`parsers.SchemaYAMLParser`,
                     `parsers.SchemaCLIParser`
                     or dict):                parsed YAML, CLI or
                                              dict with necessary keys
            output                     (str): output description
            num_rows                   (int): number of rows to generate
            timeseries                (bool): whether to generate a timeseries
            records                   (list): generated data
            fake               (faker.Faker): Faker object to generate data

        Parser parameters:

            schema          (dict): dictionary of column names and
                                    values to use
                                    (i.e. {'foo': 'faker.name',...})
            num_rows         (int): number of rows to generate
            start_time  (datetime): datetime to start from if timeseries
            increments       (str): if timeseries, you may define the
                                    type of increments you want based
                                    on a series of string choices
                                    ('days', 'hours', 'seconds', 'random')
            end_time    (datetime): optional end date if timeseries

        see also `parsers.core`
    """

    FILE_REGEX = r'file://(?P<filename>.*)'
    EVAL_REGEX = [r'range\(-?\d+,-?\d+\)$',
                  r'arange\(-?\d+(\.\d+)?,-?\d+(\.\d+)?\)$']

    def __init__(self, schema_parser):
        if isinstance(schema_parser, dict):
            schema_parser = AttributeDict(schema_parser)
        self.parser = schema_parser
        self.schema = schema_parser.schema
        self.output = schema_parser.output
        self.num_rows = schema_parser.num_rows
        try:
            self.timeseries = schema_parser.start_time is not None
        except KeyError:
            self.timeseries = False
        self.records = []
        self.data_type = 'list'
        self.fake = Faker()

    def generate(self):
        """ Generate the dataset (self.records) based on
            the given schema.

            If a timeseries is selected, this method
            will pass to `Generator.generate_timeseries`
        """
        if self.timeseries:
            self.generate_timeseries()

        else:
            while len(self.records) < self.num_rows:
                row = self.generate_row()
                self.records.append(row)

    def generate_row(self):
        """ Generate a row based on the parsed schema

            NOTE: this uses string matching to determine
            if the schema is a list, faker definition
            or one of the matching patterns in
            `EVAL_REGEX` and then generates data based on
            those predefined selections.
        """
        row = {}
        for field_name, field_val in self.schema.items():
            if isinstance(field_val, str):
                for pattern in self.EVAL_REGEX:
                    if re.match(pattern, field_val):
                        field_val = eval(field_val)
                        break
            if isinstance(field_val, str) and 'faker.' in field_val:
                field_val = field_val.replace('faker.', '')
                row[field_name] = getattr(self.fake, field_val)()
            elif isinstance(field_val, collections.Iterable):
                row[field_name] = random.choice(field_val)
        return row

    def generate_timeseries(self):
        """ Generate a timeseries with a `timestamp` column.

            This uses the parser start date and increments to

            NOTE: a warning will be logged if there is an
            endtime given and the number of rows is not reached before
            the endtime. Endtime takes precedence if specified.

            TODO: should num_rows take precedence over end time?
        """

        def done(start_time, parser):
            """ return boolean to see if enough rows are generated """
            try:
                if parser.end_time:
                    return start_time >= parser.end_time
            except KeyError:
                pass
            return len(self.records) >= parser.num_rows

        start_time = self.parser.start_time

        while not done(start_time, self.parser):
            row = self.generate_row()
            row['timestamp'] = start_time.isoformat()
            self.records.append(row)
            start_time += self.increment_time()

        if len(self.records) < self.num_rows:
            logging.warning(
                'With given end time, datafuzz did not ' +
                'generate required # of rows.')

    def increment_time(self):
        """ For timeseries generation, increment the start time
            given the parser requirements:
                - hours, days, seconds
                - if not set, returns random mix

            TODO: allow for set interval?
        """
        increment = self.parser.increments
        if increment == 'hours':
            return timedelta(hours=random.randint(1, 10))
        elif increment == 'days':
            return timedelta(days=random.randint(1, 5))
        elif increment == 'seconds':
            return timedelta(seconds=random.randint(20, 50))
        return timedelta(days=random.randint(1, 3),
                         hours=random.randint(1, 10),
                         seconds=random.randint(3, 65))

    @property
    def output_filename(self):
        """ Return filename if output follows proper file format
            file://[absolute or relative filepath]
        """
        return re.match(self.FILE_REGEX, self.output).group('filename')

    def to_output(self):
        """ Return or create output based on parsed schema.
        """
        return obj_to_output(self)
