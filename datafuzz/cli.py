# -*- coding: utf-8 -*-
"""Console script for datafuzz."""
import argparse
import sys
from datafuzz.parsers import StrategyCLIParser, StrategyYAMLParser, \
    SchemaCLIParser, SchemaYAMLParser


def main(args=None):
    """Console script for datafuzz.

    This attempts to determine which parser to use with the initial arguments.

    Default will load the YAML Parser, which will take either run or generate
    and the yaml file.

    Alternatively, it will try the CLI parsers, using the first argument
    (run or genrate) as a switch.

    If arguments are properly parsed and loaded, it will execute the generation
    or run strategy to completion.
    """
    if args is None:
        args = sys.argv[1:]
    if not args or (len(args) < 3 and '--non-yaml' not in args):
        parser = get_init_parser()
    elif args[0] == 'run':
        parser = StrategyCLIParser()
    elif args[0] == 'generate':
        parser = SchemaCLIParser()
    else:
        parser = get_init_parser()

    try:
        args = parser.parse_args(args)
    except AttributeError:
        parser.print_help()

    try:
        if isinstance(parser, argparse.ArgumentParser):
            parser = get_yaml_parser(args)
        output = parser.execute()
        print('dataset now available at', output)
    except Exception as e:
        print('Encountered error while running: %s' % e)


def get_init_parser():
    """ Generate default initial parser with only
        arguments for YAML parser.
            -type: 'run' or 'generate'
            -file_name: YAML to parse
            --non-yaml: flag to see non-yaml help

        Returns `argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser(
        description='Generate or run strategies on a dataset using datafuzz')
    parser.add_argument('type', choices=['run', 'generate'], type=str,
                        help="Run strategies on a dataset or " +
                        "generate a new dataset with schema.")
    parser.add_argument('file_name', type=str,
                        help="YAML with strategies or schema.")
    parser.add_argument('--non-yaml', action='store_true',
                        help="show non-yaml options (you must define run or generate)")
    return parser


def get_yaml_parser(init_parser):
    """ Return StrategyYAMLParser or SchemaYAMLParser
        from initial parser parameters.

        Uses init_parser.type

        If type == `run`: return StrategyYAMLParser
        If type == `generate`: return SchemaYAMLParser
    """
    if init_parser.type == 'run':
        return StrategyYAMLParser(init_parser.file_name)
    return SchemaYAMLParser(init_parser.file_name)


if __name__ == "__main__":
    main(sys.argv[1:])
