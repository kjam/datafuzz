import pytest
import os
import pandas as pd

from datafuzz.generators import DatasetGenerator
from datafuzz.parsers import SchemaYAMLParser

BASE_DIR = os.path.abspath(
    os.path.join(__file__, os.pardir, os.pardir, os.pardir, 'datafuzz/'))


@pytest.mark.parametrize('input_parser', [
    SchemaYAMLParser(os.path.join(BASE_DIR, 'examples/yaml_files/iot_schema.yaml')),
    SchemaYAMLParser(os.path.join(BASE_DIR, 'examples/yaml_files/sales_schema.yaml')),
    SchemaYAMLParser(os.path.join(BASE_DIR, 'examples/yaml_files/sales_schema_timeseries.yaml')),
])
def test_init(input_parser):
    ds_generator = DatasetGenerator(input_parser)
    assert isinstance(ds_generator, DatasetGenerator)
    assert isinstance(ds_generator.schema, dict)
    assert ds_generator.output
    assert ds_generator.num_rows
    assert ds_generator.fake
    assert isinstance(ds_generator.records, list)
    if ds_generator.timeseries:
        assert ds_generator.parser.start_time


@pytest.mark.parametrize('input_parser', [
    SchemaYAMLParser(os.path.join(BASE_DIR, 'examples/yaml_files/iot_schema.yaml')),
    SchemaYAMLParser(os.path.join(BASE_DIR, 'examples/yaml_files/sales_schema.yaml')),
    SchemaYAMLParser(os.path.join(BASE_DIR, 'examples/yaml_files/sales_schema_timeseries.yaml')),
])
def test_generate(input_parser):
    ds_generator = DatasetGenerator(input_parser)
    ds_generator.generate()
    assert isinstance(ds_generator, DatasetGenerator)
    assert isinstance(ds_generator.schema, dict)
    assert isinstance(ds_generator.records, list)
    if not ds_generator.timeseries:
        assert len(ds_generator.records) == ds_generator.num_rows
    assert isinstance(ds_generator.records[0], dict)
    if not ds_generator.timeseries:
        assert sorted(list(ds_generator.records[0].keys())) == sorted(list(ds_generator.schema.keys()))
    else:
        assert sorted(list(ds_generator.records[0].keys())) == sorted(list(ds_generator.schema.keys()) + ['timestamp'])


@pytest.mark.parametrize('input_parser', [
    SchemaYAMLParser(os.path.join(BASE_DIR, 'examples/yaml_files/iot_schema.yaml')),
    SchemaYAMLParser(os.path.join(BASE_DIR, 'examples/yaml_files/sales_schema.yaml')),
    SchemaYAMLParser(os.path.join(BASE_DIR, 'examples/yaml_files/sales_schema_timeseries.yaml')),
])
def test_to_output(input_parser):
    ds_generator = DatasetGenerator(input_parser)
    ds_generator.generate()
    output = ds_generator.to_output()
    if ds_generator.output == 'list':
        assert isinstance(output, list)
    elif ds_generator.output == 'pandas':
        assert isinstance(output, pd.DataFrame)
    elif ds_generator.output.startswith('file'):
        assert os.path.exists(output)
