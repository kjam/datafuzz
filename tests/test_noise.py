import collections
import pytest
import pandas as pd
import numpy as np

from datafuzz.dataset import DataSet
from datafuzz.noise import NoiseMaker


@pytest.mark.parametrize('input_obj,cols', [
    ([[1, 2, 3], [4, 5, 6]], ['2']),
    ([[1, 2, 3], [4, 5, 6]], None),
    (pd.DataFrame([{'test': 12, 'idx': 1},
                   {'test': 12.3, 'idx': 2}]), ['idx']),
    (pd.DataFrame([{'test': 12, 'idx': 1},
                   {'test': 12.3, 'idx': 2}]), None),
    (np.random.rand(3, 2), [0,1]),
    (np.random.rand(3, 2), None),
])
def test_init(input_obj, cols):
    dataset = DataSet(input_obj)
    noizer = NoiseMaker(dataset, **{'columns': cols, 'percentage': 50, 'noise': ['random']})
    assert isinstance(noizer, NoiseMaker)
    assert isinstance(noizer.columns, collections.Iterable)
    assert noizer.num_rows > 0
    assert noizer.percentage == .5

    with pytest.raises(Exception):
        NoiseMaker(dataset, **{'columns': cols, 'percentage': 50})


@pytest.mark.parametrize('input_obj,cols,noise,limits', [
    ([[1, 2, 3], [4, 5, 6]], ['2'], ['add_nulls', 'random', 'range'], None),
    ([[1, 2, 3], [4, 5, 6]], None, ['type_transform'], None),
    ([[1, 2, '1'], [4, 5, '6']], [2], ['type_transform'], None),
    ([[1, 2, 3.3], [4, 5, 6.5]], [2], ['type_transform'], None),
    (pd.DataFrame([{'testnum': 12, 'test': 'here is a string!', 'idx': 1},
                   {'testnum': 12.3, 'test': 'another one ! With Capitals!', 'idx': 2}]), ['test'], ['string_permutation'], None),
    (pd.DataFrame([{'testnum': 12, 'test': 'here is a string!', 'idx': 1},
                   {'testnum': 12.3, 'test': 'another one ! With Capitals!', 'idx': 2}]), ['test'], ['random'], None),
    (pd.DataFrame([{'testnum': 12, 'idx': 1},
                   {'testnum': 12.3, 'idx': 2}]), None, ['range', 'add_nulls'], [0, 12]),
    (np.random.rand(3, 2), [0,1], ['random', 'type_transform'], None),
    (np.random.rand(3, 2), None, ['add_nulls'], None),
])
def test_run_strategy(input_obj, cols, noise, limits):
    if isinstance(input_obj, list):
        dataset = DataSet(input_obj, pandas=False)
    else:
        dataset = DataSet(input_obj)
    noizer = NoiseMaker(dataset, **{'columns': cols, 'percentage': 50, 'noise': noise}, limits=limits)
    noizer.run_strategy()
    assert isinstance(noizer, NoiseMaker)
    assert isinstance(noizer.columns, collections.Iterable)
    if dataset.data_type == 'pandas':
        assert not dataset.records.equals(dataset.input)
    elif dataset.data_type == 'numpy':
        assert not np.array_equal(dataset.records, dataset.input)
    else:
        assert dataset.records != dataset.input


@pytest.mark.parametrize('input_obj,cols,val', [
    ([[1, 2, 3], [4, 5, 6]], ['2'], 0),
    (pd.DataFrame([{'testnum': 12, 'test': 'here is a string!', 'idx': 1},
                   {'testnum': 12.3, 'test': 'another one ! With Capitals!', 'idx': 2}]), ['test'], 'foo'),
    (np.random.rand(3, 2), None, 0),
])
def test_set_value(input_obj,cols,val):
    if isinstance(input_obj, list):
        dataset = DataSet(input_obj, pandas=False)
    else:
        dataset = DataSet(input_obj)
    noizer = NoiseMaker(dataset, **{'columns': cols, 'percentage': 50, 'noise': ['random']})
    noizer.set_value(val)
    for col in noizer.columns:
        if noizer.dataset.data_type == 'pandas':
            assert noizer.dataset.records[noizer.dataset.records.iloc[:,col] == val].shape[0] >= 1
        elif noizer.dataset.data_type == 'numpy':
            assert val in noizer.dataset.records[:,col]
        else:
            assert val in [r[col] for r in noizer.dataset.records]
