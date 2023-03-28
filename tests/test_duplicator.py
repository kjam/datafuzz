import collections
import pytest
import numpy as np
import pandas as pd
from datafuzz.duplicator import Duplicator
from datafuzz.dataset import DataSet

@pytest.mark.parametrize('input_obj', [
    [[1, 2, 3], [4, 5, 6]],
    pd.DataFrame([{'test': 12, 'str_col': 'Testing duplication',  'idx': 1},
                  {'test': 12.3, 'str_col': 'Another row', 'idx': 2}]),
    np.random.rand(3, 2),
])
def test_init(input_obj):
    if isinstance(input_obj, list):
        dataset = DataSet(input_obj, pandas=False)
    else:
        dataset = DataSet(input_obj)
    duper = Duplicator(dataset, **{'percentage': 50})
    assert isinstance(duper, Duplicator)
    assert duper.num_rows > 0

@pytest.mark.parametrize('input_obj', [
    [[1, 2, 3], [4, 5, 6]],
    pd.DataFrame([{'test': 12, 'str_col': 'Testing duplication',  'idx': 1},
                  {'test': 12.3, 'str_col': 'Another row', 'idx': 2}]),
    np.random.rand(3, 2),
])
def test_duplicate(input_obj):
    if isinstance(input_obj, list):
        dataset = DataSet(input_obj, pandas=False)
    else:
        dataset = DataSet(input_obj)
    duper = Duplicator(dataset, **{'percentage': 50})
    duper.run_strategy()
    assert isinstance(duper, Duplicator)
    if dataset.data_type == 'pandas':
        assert not dataset.records.equals(dataset.input)
        assert dataset.records.duplicated().any()
        assert len(dataset) > dataset.input.shape[0]
    elif dataset.data_type == 'numpy':
        unique = np.unique(dataset.records, axis=0)
        assert sorted(unique.ravel()) == sorted(dataset.input.ravel())
        assert not np.array_equal(dataset.records, dataset.input)
        assert len(dataset) > dataset.input.shape[0]
    else:
        counter = collections.Counter([str(r) for r in dataset.records])
        assert any([val if val[1] > 1 else None for val in counter.most_common()])
        assert dataset.records != dataset.input
        assert len(dataset) > len(dataset.input)


@pytest.mark.parametrize('input_obj', [
    [[1, 2, 3, 4], [42, 15, 36, 55], [32, 4444, 48932, 217839]],
    pd.DataFrame([{'test': -22.3, 'str_col': 'Testing duplication',  'idx': 1, 'bar': np.nan},
                  {'test': 124.3, 'str_col': 'Another row', 'idx': 2, 'bar': 0}]),
    np.random.rand(3, 2),
])
def test_duplicate_with_noise(input_obj):
    if isinstance(input_obj, list):
        dataset = DataSet(input_obj, pandas=False)
    else:
        dataset = DataSet(input_obj)
    duper = Duplicator(dataset, **{'percentage': 50, 'add_noise': True})
    duper.run_strategy()
    print(dataset.records)
    assert isinstance(duper, Duplicator)
    if dataset.data_type == 'pandas':
        assert not dataset.records.equals(dataset.input)
        assert not dataset.records.duplicated().any()
    elif dataset.data_type == 'numpy':
        assert not np.array_equal(np.unique(dataset.records, axis=0), dataset.input)
        assert not np.array_equal(dataset.records, dataset.input)
    else:
        counter = collections.Counter([str(r) for r in dataset.records])
        assert not any([val if val[1] > 1 else None for val in counter.most_common()])
        assert dataset.records != dataset.input
