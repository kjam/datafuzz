import os
import pytest
import collections
import dataset as dataset_db

from datafuzz.dataset import DataSet

import pandas as pd
import numpy as np


@pytest.mark.parametrize('input_obj',[
    [{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}],
     pd.DataFrame([{'test': 1.23, 'foo': 444},
                   {'test': np.nan, 'foo': 123}]),
     np.random.rand(2,2)])
def test_init_from_obj(input_obj):
    data = DataSet(input_obj)
    if isinstance(input_obj, list):
        assert data.records.equals(pd.DataFrame(input_obj))
        assert data.original == input_obj
    elif isinstance(input_obj, pd.DataFrame):
        assert data.records.equals(input_obj)
        assert data.input.equals(input_obj)
        assert data.original.equals(input_obj)
    else:
        assert np.array_equal(data.original, input_obj)
        assert np.array_equal(data.records, input_obj)
        assert np.array_equal(data.input, input_obj)
    assert data.records is not input_obj
    assert data.original is input_obj
    assert len(data) == 2
    assert isinstance(data, collections.Iterable)

    count = 0
    for line in data:
        if data.data_type == 'pandas':
            assert data[count].equals(data.records.iloc[count,:])
        elif data.data_type == 'numpy':
            assert np.array_equal(data[count], data.records[count, :])
        else:
            assert data[count] == line
        count += 1
    assert count == 2


@pytest.mark.parametrize('input_obj,kwargs',[
 ('sql', {'db_uri': 'sqlite:///tests/data/test_db.db', 'query': "SELECT * from customers;"}),
 ('sql', {'db_uri': 'sqlite:///tests/data/test_db.db', 'query': "SELECT * from customers;", 'pandas': False}),
 ([[1,2,3]], {'output': 'sql', 'db_uri': 'sqlite:///:memory:', 'table': 'customers'}),
 ])
def test_init_sql(input_obj,kwargs):
    data = DataSet(input_obj, **kwargs)
    assert isinstance(data, DataSet)
    assert data.db_uri == kwargs.get('db_uri')
    assert data.query == kwargs.get('query')
    if kwargs.get('pandas') is None:
        assert isinstance(data.input, pd.DataFrame)
    else:
        assert isinstance(data.input, list)


@pytest.mark.parametrize('input_file,shape',[
    ('tests/data/test_csv.csv', (3,3)),
    ('tests/data/test_json.json', (3,4)),
])
def test_init_from_file(input_file, shape):
    filename = 'file://{}'.format(input_file)
    data = DataSet(filename)
    assert data.records is not input_file
    assert data.input is not input_file
    assert data.data_type == 'pandas'
    assert isinstance(data.records, pd.DataFrame)
    assert isinstance(data.input, pd.DataFrame)
    assert data.records.shape == shape
    assert data.input.shape == shape
    assert data.original == filename
    assert data.input_filename == filename.replace('file://', '')


@pytest.mark.parametrize('input_obj, shape', [
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], (2,3)),
    ('tests/data/test_csv.csv', (3,3)),
    ('tests/data/test_json.json', (3,4))
])
def test_init_no_pandas(input_obj, shape):
    if isinstance(input_obj, str):
        input_obj = 'file://{}'.format(input_obj)
    data = DataSet(input_obj, pandas=False)
    assert isinstance(data.records, list)
    assert isinstance(data.input, list)
    assert len(data.records) == shape[0]
    assert len(data.records[0]) == shape[1]
    assert data.original == input_obj


@pytest.mark.parametrize('input_obj,error', [
    ('mystring: foo, bar, baz', TypeError),
    ({'a': 1, 'b': 2}, TypeError),
    ([], Exception),
])
def test_init_errors(input_obj, error):
    with pytest.raises(error):
        DataSet(input_obj)


@pytest.mark.parametrize('input_obj,output,output_type,kwargs',[
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], 'list', list, {}),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], 'pandas', pd.DataFrame, {}),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], 'pandas', pd.DataFrame, {'pandas': False}),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], 'numpy', np.ndarray, {}),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], 'numpy', np.ndarray, {'pandas': False}),
    (np.array([[1,2,3], [4,5,6]]), 'list', list, {}),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], 'file:///tmp/test.csv', str, {}),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], 'file:///tmp/test.json', str, {}),
])
def test_output(input_obj, output, output_type, kwargs):
    data = DataSet(input_obj, output=output, **kwargs)
    if output.startswith('file://'):
        assert data.output_filename == output.replace('file://', '')
    to_output = data.to_output()
    assert isinstance(to_output, output_type)
    if output_type == list and isinstance(input_obj, list):
        assert input_obj == to_output
    elif output_type == list:
        assert input_obj.tolist() == to_output
    elif output_type == pd.DataFrame:
        assert to_output.shape == (2,3)
    elif output_type == np.ndarray and not kwargs:
        assert np.array_equal(to_output[0,:], [1,2,5])
    elif output_type == np.ndarray:
        assert to_output[0] == {'a': 1, 'b': 2, 'd': 5}
    elif output_type == str:
        assert os.path.exists(to_output)


@pytest.mark.parametrize('input_obj,output',[
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], 'xjfkl'),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], 'file:///tmp/foo.txt'),
])
def test_output_errors(input_obj, output):
    with pytest.raises(NotImplementedError):
        data = DataSet(input_obj, output=output)
        data.to_output()

@pytest.mark.parametrize('input_obj,output,kwargs',[
    ('file:///tmp/o.csv', '', {}),
    ('', '', {}),
    ('tests/data/test_csv.csv', 'file:////\0xmy_test.csv', {}),
    ('tests/data/bad_json.json', '', {'pandas': False}),
    ([[1,2,3]], 'sql', {}),
])
def test_bad_io(input_obj, output, kwargs):
    with pytest.raises(Exception):
        if 'data' in input_obj:
            input_obj = 'file://{}'.format(input_obj)
        data = DataSet(input_obj, output=output, **kwargs)
        data.to_output()


@pytest.mark.parametrize('input_obj,percentage,columns,kwargs',[
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], .5, False, {}),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], .3, True, {}),
    (np.array([[1, 2, 3], [4, 5, 6]]), .5, False, {}),
    (np.array([[0, 1, 2], [0, 1, 2]]), .3, True, {}),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], .5, False, {'pandas': False}),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], .3, True, {'pandas': False}),
])
def test_sample(input_obj, percentage, columns, kwargs):
    data = DataSet(input_obj, **kwargs)
    sample = data.sample(percentage, columns=columns)
    assert len(sample) == 1
    if columns and not kwargs:
        assert sample[0] in input_obj[0]
    elif columns:
        assert sample[0] in [0,1,2]
    elif isinstance(sample, pd.DataFrame):
        assert list(sample.T.to_dict().values())[0] in input_obj
    else:
        assert sample[0] in input_obj


@pytest.mark.parametrize('input_obj,rows,shape,kwargs',[
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}],
     [{'a': 6, 'b': 50, 'd': 88}], (3, 3), {}),
    (np.array([[1,2,3], [4,3,5]]), [[2,3,3]], (3, 3), {}),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}],
     pd.DataFrame([{'a': 6, 'b': 50, 'd': 88}]), (3, 3), {}),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}],
     [{'a': 6, 'b': 50, 'd': 88}], (3, 3), {'pandas': False}),
])
def test_append(input_obj, rows, shape, kwargs):
    data = DataSet(input_obj, **kwargs)
    data.append(rows)
    if data.data_type in ['numpy', 'pandas']:
        assert data.records.shape == shape
    else:
        assert len(data.records) == shape[0]
        assert len(data.records[0]) == shape[1]



@pytest.mark.parametrize('input_obj,column,col_type,kwargs',[
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], 'b', np.int64, {}),
    (np.array([[1,2,3], [4,3,5]]), 2, np.int64, {}),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], 'b', int, {'pandas': False}),
])
def test_column_dtype(input_obj, column, col_type, kwargs):
    data = DataSet(input_obj, **kwargs)
    if isinstance(column, str):
        column = data.column_idx(column)
    assert data.column_dtype(column) == col_type


@pytest.mark.parametrize('input_obj,column,agg,result,kwargs',[
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], 'b', sum, 7, {}),
    (np.array([[1,2,3], [4,3,5]]), 0, max, 4, {}),
    ([{'a': 1, 'b': 2, 'd': 5},
      {'a': 4, 'b': 5, 'd': 90}], 'b', min, 2, {'pandas': False}),
])
def test_column_agg(input_obj, column, agg, result, kwargs):
    data = DataSet(input_obj, **kwargs)
    if isinstance(column, str):
        column = data.column_idx(column)
    assert data.column_agg(column, agg) == result
