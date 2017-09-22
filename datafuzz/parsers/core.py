# -*- coding: utf-8 -*-
"""
YAML and CLI parsers
"""
import argparse
import json
import logging
from datetime import datetime
import yaml

from datafuzz.parsers.helpers import generate_from_parser, fuzz_from_parser


class BaseYAMLParser:
    """ Base YAML Parser class

        Parameters:
            file_path (str): file to parse

        Attributes:
            REQUIRED_FIELDS (dict): dictionary of required fields
            file_path        (str): file to parse
    """
    REQUIRED_FIELDS = {}

    def __init__(self, file_path):
        self.file_path = file_path
        self.parse()

    def parse(self):
        """ Parse the file and validate the parsed YAML

            raises SyntaxError if bad YAML
        """
        with open(self.file_path, 'r') as myf:
            try:
                self.parsed = yaml.load(myf)
            except yaml.YAMLError:
                logging.exception('Error loading YAML file')
                raise SyntaxError('Invalid YAML! Please correct your syntax.')
        self.validate_yaml()

    def validate_yaml(self):
        """ Ensure all required fields are parsed
            and exist

            Note: Uses dictionary self.REQUIRED_FIELDS

            raises SyntaxError if fields missing
        """
        for section, fields in self.REQUIRED_FIELDS.items():
            try:
                values = self.parsed.get(section)
                assert values is not None
                if isinstance(values, dict):
                    assert all([values.get(f) for f in fields])
                elif isinstance(values, list):
                    for value_row in values:
                        assert set(fields).issubset(set(value_row.keys()))
            except AssertionError:
                raise SyntaxError(
                    'Your YAML file does not have all required fields. ' +
                    'Required fields: {}'.format(self.REQUIRED_FIELDS)
                )


class StrategyYAMLParser(BaseYAMLParser):
    """ Strategy YAML Parser is used
        to parse strategies and fuzz / transform
        data using a simple YAML definition.

        see also `parsers.core.BaseYAMLParser`
    """

    REQUIRED_FIELDS = {
        'data': ['input', 'output'],
        'strategies': ['type', 'percentage']
    }

    @property
    def strategies(self):
        """ Return strategies from parsed YAML """
        return self.parsed.get('strategies')

    @property
    def input(self):
        """ Return data input from parsed YAML """
        return self.parsed.get('data').get('input')

    @property
    def output(self):
        """ Return data output from parsed YAML """
        return self.parsed.get('data').get('output')

    @property
    def db_uri(self):
        """ Return data db_uri from parsed YAML """
        return self.parsed.get('data').get('db_uri')

    @property
    def table(self):
        """ Return data table from parsed YAML """
        return self.parsed.get('data').get('table')

    @property
    def query(self):
        """ Return data query from parsed YAML """
        return self.parsed.get('data').get('query')

    def execute(self):
        """ Execute strategies from parsed YAML """
        return fuzz_from_parser(self)


class StrategyCLIParser:
    """ Strategy YAML CLI is used
        to parse strategies and fuzz / transform
        data using a simple CLI definition.
    """

    REQUIRED_FIELDS = ['output', 'input', 'strategies']

    def __init__(self, **kwargs):
        """ Parse arguments for fuzzing data

            Attributes:
                input      (str): filename or "sql" for input data
                output     (str): filename or "sql" for output data
                strategies (str): dict outlining strategies for noise,
                                  duplication, etc
                db_uri     (str): if using database (input or out),
                                  database uri to connect
                query      (str): if using database input, query to execute
                table      (str): if using database output,
                                                       table name to insert

        Note: strategies should have all required fields
              see `strategy.Strategy`

        """
        self.input = kwargs.get('input')
        self.output = kwargs.get('output')
        self.strategies = kwargs.get('strategies')
        self.db_uri = kwargs.get('db_uri')
        self.query = kwargs.get('query')
        self.table = kwargs.get('table')
        self.parser = self.init_parser()

    def validate_arguments(self):
        """ Validate that all required fields are submitted """
        for section in self.REQUIRED_FIELDS:
            assert getattr(self, section) is not None

    def init_parser(self):
        """ Initialize parser with required and optional arguments

            Returns:
                argparse.ArgumentParser
        """
        parser = argparse.ArgumentParser(
            description='Apply datafuzz strategies to input, return output')
        parser.add_argument('run', choices=['run'], default='run')
        parser.add_argument('-i', '--input', type=str,
                            help='input string (filename or sql)')
        parser.add_argument('-o', '--output', type=str,
                            help='input string (filename or sql)')
        parser.add_argument('-s', '--strategies', type=json.loads,
                            help='dictionary defining the strategies to take')
        parser.add_argument('--db_uri',
                            type=str,
                            help='If using database, the db URI to connect')
        parser.add_argument('--query',
                            type=str,
                            help='If using db input, query to collect data')
        parser.add_argument('--table', type=str,
                            help='If using db output, table to insert into')
        return parser

    def parse_args(self, argv=None):
        """ Parse arguments and validate them

            Kwargs:
                argv (sys.argv or similar list)
        """
        args = self.parser.parse_args(argv)
        self.input = args.input
        self.output = args.output
        self.strategies = args.strategies
        if not isinstance(self.strategies, list):
            self.strategies = [self.strategies]
        self.db_uri = args.db_uri
        self.query = args.query
        self.table = args.table
        self.validate_arguments()

    def print_help(self):
        """ print parser help """
        self.parser.print_help()

    def execute(self):
        """ execute fuzzing strategies from parser

            Returns:
                output
        """
        return fuzz_from_parser(self)


class SchemaYAMLParser(BaseYAMLParser):
    """ Schema YAML Parser is used
        generate data using a simple YAML definition.

        see also `parsers.core.BaseYAMLParser`
    """

    REQUIRED_FIELDS = ['schema', 'output', 'num_rows']

    def __init__(self, file_name):
        """ Parse the schema for generating data

            (see: `parser.BaseYAMLParser`)

            Attributes:
                start_time (datetime): start date for timeseries (or None)
                end_time   (datetime): end date for timeseries (or None)
                increments      (str): timeseries increment
                                       'seconds', 'hours', 'days' (or None)

        """
        super().__init__(file_name)
        self.start_time = None
        self.end_time = None
        self.increments = None
        if 'timeseries' in self.parsed:
            self.parse_timeseries()

    @property
    def schema(self):
        """ Return schema from parsed YAML """
        return self.parsed.get('schema')

    @property
    def output(self):
        """ Return output from parsed YAML """
        return self.parsed.get('output')

    @property
    def timeseries(self):
        """ Return timeseries from parsed YAML """
        return self.parsed.get('timeseries')

    @property
    def num_rows(self):
        """ Return num_rows from parsed YAML """
        return self.parsed.get('num_rows')

    def validate_yaml(self):
        """ Validate that all required fields are parsed from YAML

            raises SyntaxError if required field missing
        """
        for section in self.REQUIRED_FIELDS:
            try:
                assert self.parsed.get(section) is not None
            except AssertionError:
                raise SyntaxError(
                    'Required field {} is not present!'.format(section))

    def parse_timeseries(self):
        """ Parse and set values related to timeseries

            raises SyntaxError if start or end time were
            not properly parsed
        """
        self.start_time = self.timeseries.get('start_time')
        self.end_time = self.timeseries.get('end_time')
        self.increments = self.timeseries.get('increments')
        if isinstance(self.start_time, datetime):
            if self.end_time is None or isinstance(self.end_time, datetime):
                return
        raise SyntaxError(
            'You must specify starttime in isoformat: ' +
            'YYYY-MM-DDThh:mm or YYYY-MM-DDThh:mm:ss')

    def execute(self):
        """ generate data using parsed YAML

            Returns:
                output
        """
        return generate_from_parser(self)


class SchemaCLIParser:
    """ Schema Parser for CLI Input
        This generates a argparser to parse input
        and can be used to then generate the
        dataset
    """

    REQUIRED_FIELDS = ['output', 'num_rows', 'schema']

    def __init__(self, **kwargs):
        """ Parse arguments for generating data

            Attributes:
                start_time     (datetime): start date for timeseries (or None)
                end_time       (datetime): end date for timeseries (or None)
                increments          (str): timeseries increment
                                          'seconds', 'hours', 'days' (or None)
                num_rows            (int): number of rows to generate
                output              (str): output string (filename)
                schema              (dict): dictionary of schema to generate
                parser  (`ArgumentParser`): argument parser

        Note: length of fields should match that of values

        """
        self.num_rows = kwargs.get('num_rows')
        self.start_time = kwargs.get('start_time')
        self.end_time = kwargs.get('end_time')
        self.increments = kwargs.get('increments')
        self.output = kwargs.get('output')
        self.schema = kwargs.get('schema') or {}
        self.parser = self.init_parser()

    def validate_arguments(self):
        """ Validate that all required fields are submitted """
        for section in self.REQUIRED_FIELDS:
            try:
                assert getattr(self, section) is not None
            except AssertionError:
                raise Exception("You must include %s in your parser" % section)

    def init_parser(self):
        """ Generate `argparse.ArgumentParser`
            to use for parsing arguments """
        parser = argparse.ArgumentParser(
            description='Generate dataset: to use')
        parser.add_argument('generate', choices=['generate'],
                            default='generate')
        parser.add_argument('-f', '--fields', type=lambda x: x.split(';'),
                            help='semicolon-delimited string of field names')
        parser.add_argument('-v', '--values', type=lambda x: x.split(';'),
                            help='semicolon-delimited string of values.' +
                            'This can be a mix of faker types and ranges')
        parser.add_argument('-o', '--output', type=str,
                            help='what output to use')
        parser.add_argument('-n', '--num_rows', type=int,
                            help='number of rows to generate')
        parser.add_argument('--start_time',
                            type=lambda x:
                            datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'),
                            help='start time of timeseries in isoformat:' +
                            'YYYY-MM-DDThh:mm:ss')
        parser.add_argument('--end_time',
                            type=lambda x:
                            datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'),
                            help='end time of timeseries in isoformat: ' +
                            'YYYY-MM-DDThh:mm:ss')
        parser.add_argument('--increments',
                            choices=['hours', 'seconds', 'days', 'random'],
                            default='random',
                            help='how to increment entries')
        return parser

    def parse_args(self, argv=None):
        """ Parse arguments and validate them

            Kwargs:
                argv (sys.argv or similar list)
        """
        args = self.parser.parse_args(argv)
        self.start_time = args.start_time
        self.end_time = args.end_time
        self.increments = args.increments
        self.num_rows = args.num_rows
        self.output = args.output
        self.schema = dict((f, v) for f, v in zip(args.fields, args.values))
        self.validate_arguments()

    def print_help(self):
        """ print parser help """
        self.parser.print_help()

    def execute(self):
        """ Generates data from CLI parsed arguments

            Returns:
                output
        """
        return generate_from_parser(self)
