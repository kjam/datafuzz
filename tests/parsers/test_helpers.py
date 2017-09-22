import pytest
import numpy as np

from datafuzz.parsers.helpers import build_strategy, fuzz_from_parser, generate_from_parser
from datafuzz.parsers.core import StrategyYAMLParser, SchemaYAMLParser, StrategyCLIParser, SchemaCLIParser
from datafuzz.fuzz import Fuzzer
from datafuzz.noise import NoiseMaker
from datafuzz.duplicator import Duplicator
from datafuzz.dataset import DataSet


def test_generate_from_parser():
    parser = SchemaYAMLParser('datafuzz/examples/yaml_files/iot_schema.yaml')
    output = generate_from_parser(parser)
    assert parser.output.replace('file://', '') == output

def test_fuzz_from_parser():
    parser = StrategyYAMLParser('datafuzz/examples/yaml_files/read_csv_and_dupe.yaml')
    output = fuzz_from_parser(parser)
    assert parser.output.replace('file://', '') == output

@pytest.mark.parametrize('input_dict,output,percent,cols',[
    ({'type': 'fuzz', 'percentage': 50}, Fuzzer, .5, 2),
    ({'type': 'noise', 'percentage': 10, 'columns': [2, 4], 'noise': ['random']}, NoiseMaker, .1, 2),
    ({'type': 'duplicator', 'percentage': 80}, Duplicator, .8, None),
])
def test_build_strategy(input_dict,output,percent,cols):
    dataset = DataSet(np.random.rand(20,5))
    strategy_obj = build_strategy(input_dict, dataset)
    assert isinstance(strategy_obj, output)
    assert strategy_obj.percentage == percent
    if cols:
        assert len(strategy_obj.columns) == cols
