import argparse
import json
import pytest

from datafuzz.parsers import StrategyYAMLParser, SchemaYAMLParser, SchemaCLIParser, StrategyCLIParser


def test_bad_yaml():
    with pytest.raises(SyntaxError):
        StrategyYAMLParser('tests/data/bad_yaml.yaml')
    with pytest.raises(SyntaxError):
        SchemaYAMLParser('tests/data/incomplete_schema.yaml')


def test_good_yaml():
    strategy_yaml = StrategyYAMLParser('datafuzz/examples/yaml_files/read_csv_and_dupe.yaml')
    schema_yaml = SchemaYAMLParser('datafuzz/examples/yaml_files/iot_schema.yaml')
    assert isinstance(schema_yaml.parsed, dict)
    assert isinstance(strategy_yaml.parsed, dict)


def test_generator_cli():
    gen_cli = SchemaCLIParser()
    assert isinstance(gen_cli, SchemaCLIParser)
    assert isinstance(gen_cli.parser, argparse.ArgumentParser)
    gen_cli.parse_args(['generate',
                        '-f', 'test;ing',
                        '-v', 'faker.name;range(0,9)',
                        '-o', 'file:///test.csv',
                        '-n', '2000',
                        ])
    assert gen_cli.output == 'file:///test.csv'
    assert gen_cli.num_rows == 2000
    assert isinstance(gen_cli.schema, dict)
    assert sorted(list(gen_cli.schema.keys())) == ['ing', 'test']


def test_strategy_cli():
    strategy_cli = StrategyCLIParser()
    assert isinstance(strategy_cli, StrategyCLIParser)
    assert isinstance(strategy_cli.parser, argparse.ArgumentParser)
    strategy_cli.parse_args(['run',
                            '-s', json.dumps([{'type': 'noise', 'noise': ['random'],
                                             'percentage': 50}]),

                           '-i', 'file:///itest.csv',
                           '-o', 'file:///otest.csv' ])
    assert strategy_cli.output == 'file:///otest.csv'
    assert strategy_cli.input == 'file:///itest.csv'
    assert isinstance(strategy_cli.strategies, list)
    assert isinstance(strategy_cli.strategies[0], dict)
    assert sorted(list(strategy_cli.strategies[0].keys())) == ['noise', 'percentage', 'type']
