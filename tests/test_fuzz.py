import collections
import pytest
import pandas as pd
import numpy as np

from datafuzz.dataset import DataSet
from datafuzz.fuzz import Fuzzer
from datafuzz.utils.fuzz_helpers import add_format, change_encoding, to_bytes, \
        insert_boms, nanify, bigints, hexify,  \
        sql, metachars, files, delimiter, emoji


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
    fuzzer = Fuzzer(dataset, **{'columns': cols, 'percentage': 50})
    assert isinstance(fuzzer, Fuzzer)
    assert isinstance(fuzzer.columns, collections.Iterable)
    assert fuzzer.num_rows > 0
    assert fuzzer.percentage == .5


def test_helper_methods():
    dataset = DataSet([[1, 2, 3]])
    fuzzer = Fuzzer(dataset)

    assert fuzzer.fuzz_random() in [sql, metachars, files, delimiter, emoji]
    assert fuzzer.fuzz_str() in [add_format, change_encoding,
                                 to_bytes, insert_boms]
    assert fuzzer.fuzz_numeric() in [nanify, bigints, hexify]


@pytest.mark.parametrize('input_obj,cols', [
    ([[1, 2, 3], [4, 5, 6]], ['2']),
    ([[1, 2, 3], [4, 5, 6]], None),
    (pd.DataFrame([{'test': 12, 'str_col': 'Testing the fuzz.',  'idx': 1},
                   {'test': 12.3, 'str_col': 'What will this be?', 'idx': 2}]), ['str_col']),
    (pd.DataFrame([{'test': 12, 'str_col': 'Testing the fuzz.',  'idx': 1},
                   {'test': 12.3, 'str_col': 'What will this be?', 'idx': 2}]), None),
    (np.random.rand(3, 2), [0,1]),
    (np.random.rand(3, 2), None),
])
def test_run_strategy(input_obj, cols):
    if isinstance(input_obj, list):
        dataset = DataSet(input_obj, pandas=False)
    else:
        dataset = DataSet(input_obj)
    fuzzer = Fuzzer(dataset, **{'columns': cols, 'percentage': 50})
    fuzzer.run_strategy()
    assert isinstance(fuzzer, Fuzzer)
    assert isinstance(fuzzer.columns, collections.Iterable)
    # TODO: need to add test that types are not equal as sometimes they test as equals
    if dataset.data_type == 'pandas':
        assert not dataset.records.equals(dataset.input)
    elif dataset.data_type == 'numpy':
        assert not np.array_equal(dataset.records, dataset.input)
    else:
        assert dataset.records != dataset.input
