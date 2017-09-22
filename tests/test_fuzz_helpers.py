# -*- coding: utf-8 -*-
import codecs
import re
import math
import pytest
import numpy as np
from datafuzz.utils.fuzz_helpers import add_format, change_encoding, to_bytes, \
        insert_boms, nanify, bigints, hexify,  \
        sql, metachars, files, delimiter, emoji


test_strings = ['testíng', 'tÅst 123' * 40, '\n👿\n妖魔']

@pytest.mark.parametrize('input_str', test_strings)
def test_add_format(input_str):
    output_str = add_format(input_str)
    assert re.search(r'%(f|s|d|r)', output_str).group()


@pytest.mark.parametrize('input_str', test_strings)
def test_change_encoding(input_str):
    output_str = change_encoding(input_str)
    assert isinstance(output_str, bytes)
    assert output_str != input_str
    assert output_str.decode('utf-8', errors='replace') != input_str


@pytest.mark.parametrize('input_str', test_strings)
def test_to_bytes(input_str):
    output_str = to_bytes(input_str)
    assert isinstance(output_str, bytes)


@pytest.mark.parametrize('input_str', test_strings)
def test_insert_boms(input_str):
    output_str = insert_boms(input_str)
    assert output_str.startswith(str(codecs.BOM_UTF8))


test_numbers = [0, 2*23, math.pi, -9999]

@pytest.mark.parametrize('input_num', test_numbers)
def test_nanify(input_num):
    output_num = nanify(input_num)
    assert output_num != input_num
    assert output_num in [None, 'null', 'n/a', '', -1, np.nan]
    output_num = nanify(input_num, use_numpy=False)
    assert output_num in [None, 'null', 'n/a', '', -1]


@pytest.mark.parametrize('input_num', test_numbers)
def test_bigints(input_num):
    output_num = bigints(input_num)
    assert output_num != input_num
    output_num = abs(output_num)
    assert (output_num + 1) & (output_num) == 0 and output_num != 0


@pytest.mark.parametrize('input_num', test_numbers)
def test_hexify(input_num):
    output_num = hexify(input_num)
    assert output_num != input_num
    assert isinstance(int(output_num, 16), int)


def test_sql():
    output = sql('foo')
    assert output.endswith(';')
    assert 'if exists' in output or 'sleep' in output or 'DELAY' in output


def test_metachars():
    output = metachars('foo')
    assert any([x if x in output else None for x in '|*\n,>.<"\'\t;/'])


def test_files():
    output = files('foo')
    assert '/' in output or 'source' in output


def test_delimiter():
    output = delimiter('foo')
    print(output)
    assert any([x if x in output else None for x in ';,\n\r\t:'])


def test_emoji():
    emojis = re.compile('[\U0001F300-\U0001F579'
                         '\U0001F57B-\U0001F5A3'
                         '\U0001F5A5-\U0001F5FF]+')
    assert re.search(emojis, emoji('foo')).group()
