# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""
Helpers for fuzzing.
"""
import codecs
import logging
import random
from bisect import bisect
from itertools import accumulate
from datafuzz.settings import HAS_NUMPY

if HAS_NUMPY:
    import numpy as np


# STRING METHODS


def add_format(val):
    """ Insert format strings """
    idx = random.randint(0, len(val))
    format_str = '%{}'.format(random.choice(list('fdsr')))
    return val[:idx] + format_str + val[idx:]


def change_encoding(val):
    """ Return byte value with perhaps bad encoding  """
    choice = random.choice(
        ['utf-16', 'latin-1', 'windows-1250', 'iso-8859-1'])
    return val.encode(choice, errors='replace')


def to_bytes(val):
    """ Return byte value  """
    return bytes(val, encoding='utf-8')


def insert_boms(val):
    """ Insert UTF BOMs at start of string  """
    return '{}{}'.format(codecs.BOM_UTF8, val)

# NUMERIC METHODS


def nanify(val, use_numpy=True):
    """ Insert some random null values  """
    null_choices = [None, 'null', 'n/a', '', -1]
    if HAS_NUMPY and use_numpy:
        return random.choice(null_choices + [np.nan])
    return random.choice(null_choices)


def bigints(val):
    """ Return positive or negative big integers (magic #s) """
    return random.choice(
        [2**15-1, 2**31-1, 2**32-1, 2**63-1]) * random.choice([1, -1])


def hexify(val):
    """ Return hex value  """
    try:
        return hex(int(val))
    except TypeError:
        logging.error('could not hexify %s', val)
        return val


# RANDOM / NEW DATA METHODS


def sql(*args):
    """ Generate unkind sql statements """
    return random.choice([
        "WAITFOR DELAY '0:10:0';",
        "SELECT pg_sleep(600);",
        "drop table if exists customers;",
        "drop table if exists users;",
        "drop user if exists 'admin';",
        "drop user if exists 'postgres';",
    ])


def metachars(val):
    """ Join current value with metachars  """
    char = random.choice(list('|*\n,>.<"\'\t;/'))
    return char.join(list(str(val)))


def files(val):
    """ Return file paths or commands  """
    return random.choice([
        '../../',
        '/var/run',
        '/etc',
        '/tmp',
        '/root',
        'source .',
        'cat /etc/passwd'
    ])


def delimiter(val):
    """ Add one or repeating delimiters in string """
    delim = random.choice(list(';,\n\r\t:')) * random.randint(1, 5)
    return delim.join(list(str(val)))


def emoji(val):
    """
    Convert `val` to string and add a random emoji at the end

    Used from https://gist.github.com/shello/efa2655e8a7bce52f273
    """
    emoji_ranges = [
        ('\U0001F300', '\U0001F579'),
        ('\U0001F57B', '\U0001F5A3'),
        ('\U0001F5A5', '\U0001F5FF')
    ]

    # Weighted distribution
    count = [ord(r[-1]) - ord(r[0]) + 1 for r in emoji_ranges]
    weight_distr = list(accumulate(count))

    # Get one point in the multiple ranges
    point = random.randrange(weight_distr[-1])

    # Select the correct range
    emoji_range_idx = bisect(weight_distr, point)
    emoji_range = emoji_ranges[emoji_range_idx]

    # Calculate the index in the selected range
    point_in_range = point
    if emoji_range_idx is not 0:
        point_in_range = point - weight_distr[emoji_range_idx - 1]

    emoji_char = chr(ord(emoji_range[0]) + point_in_range)
    return '{} {}'.format(val, emoji_char)
