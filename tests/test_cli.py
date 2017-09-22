import argparse
import pytest

from datafuzz.parsers.core import SchemaYAMLParser, StrategyYAMLParser
from datafuzz.cli import main, get_init_parser, get_yaml_parser


def test_init_parser():
    parser = get_init_parser()
    assert isinstance(parser, argparse.ArgumentParser)
    assert parser.description
    assert 'file_name' in parser.format_help()
    assert 'run,generate' in parser.format_help()


@pytest.mark.parametrize('ptype,fn,inst',[
    ('run', 'datafuzz/examples/yaml_files/read_csv_and_dupe.yaml', StrategyYAMLParser),
    ('generate', 'datafuzz/examples/yaml_files/iot_schema.yaml', SchemaYAMLParser)
])
def test_yaml_parser(ptype, fn, inst):
    parser = get_init_parser()
    parser.type = ptype
    parser.file_name = fn
    yaml_parser = get_yaml_parser(parser)
    assert isinstance(yaml_parser, inst)


def test_main():
    # TODO: how to test prints? mock?
    main(['run', 'datafuzz/examples/yaml_files/read_csv_and_dupe.yaml'])
