import pytest
from datafuzz.utils.noise_helpers import messy_spaces, pertubate_str

input_strs = ['testing this', 'testing with spaces']

@pytest.mark.parametrize('input_str', input_strs)
def test_messy_spaces(input_str):
    assert input_str != messy_spaces(input_str)

input_strs = ['testing this', 'testing with spaces and numbers 121 !!']

@pytest.mark.parametrize('input_str', input_strs)
def test_messy_spaces(input_str):
    assert input_str != messy_spaces(input_str)
