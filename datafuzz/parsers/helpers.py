# -*- coding: utf-8 -*-
"""
Helpers for parsers: CLI and YAML implementations
"""
import logging

from datafuzz.dataset import DataSet
from datafuzz.fuzz import Fuzzer
from datafuzz.noise import NoiseMaker
from datafuzz.duplicator import Duplicator
from datafuzz.generators import DatasetGenerator


def build_strategy(strategy, dataset):
    """ Build a strategy object given
        a strategy dictionary (or similar) and dataset

        Arguments:
            strategy (dict or dict-like): strategy to apply
            dataset  (`dataset.DataSet`): dataset to use

        Returns:
            strategy object: `duplicator.Duplicator`,
                             `fuzz.Fuzzer`,
                             `noise.NoiseMaker`

        raises NotImplementedError if strategy cannot be found
    """
    percentage = strategy.get('percentage')
    columns = strategy.get('columns')
    strategy_type = strategy.get('type').lower()
    if 'fuzz' in strategy_type:
        return Fuzzer(dataset, percentage=percentage, columns=columns)
    elif 'noise' in strategy_type:
        noise = strategy.get('noise')
        return NoiseMaker(dataset, percentage=percentage,
                          columns=columns, noise=noise)
    elif 'dupli' in strategy_type or 'dupe' in strategy_type:
        return Duplicator(dataset, percentage=percentage, columns=columns)
    raise NotImplementedError('No strategy for type {}'.format(strategy_type))


def fuzz_from_parser(parser):
    """ Fuzz using parser input.
        This will generate a `dataset.Dataset` from `parser.input`,
        apply any defined strategies and call `dataset.to_output`.

        Arguments:
            parser (`parsers.StrategyCLIParser` or
                    `parsers.StrategyYAMLParser`): strategy parser

        Returns:
            dataset.to_output()
    """
    dataset = DataSet(parser.input, output=parser.output,
                      db_uri=parser.db_uri, query=parser.query,
                      table=parser.table)
    for strategy in parser.strategies:
        strategy_obj = build_strategy(strategy, dataset)
        try:
            strategy_obj.run_strategy()
        except Exception:
            logging.exception('Error running strategy: %s', strategy)
    return dataset.to_output()


def generate_from_parser(parser):
    """ Generate data using parser input.
        This will generate a dataset from `parser.schema`
        using `generators.DatasetGenerator`
        and then call `DatasetGenerator.to_output`.

        Arguments:
            parser (`parsers.SchemaCLIParser` or
                    `parsers.SchemaYAMLParser`
                    or dict with proper args): schema parser

        Returns:
            generator.to_output()
    """
    generator = DatasetGenerator(parser)
    generator.generate()
    return generator.to_output()
