# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""
Helpers for noise.
"""
import logging
import random
import re
import string

# STRING METHODS

def pertubate_str(val):
    """ Generate a random string by permutating some characters
        Arguments:
            val (str): original string

        Returns:
            str
    """ 
    possible_str = string.ascii_letters + string.punctuation + string.digits
    for _ in range(random.randrange(1, 5)):
        char = random.choice(val)
        replacement = random.choice(possible_str.replace(char, ''))
        val = val.replace(char, replacement)
    return val

def messy_spaces(val):
    """ Add or remove spaces from a string
        Arguments:
            val (str): string to manipulate
        Returns:
            str
    """
    return val.replace(' ', ' ' * random.choice([0, 2, 3, 4, 5]))

# NUMERIC METHODS

def generate_random_int(val, low=0, high=100):
    """ Generate and integer between low and high
        Arguments:
            val (value): ignored for now
        Kwargs:
            low   (int): low value (default: 0)
            low   (int): high value (default: 100)
        Returns:
            int

        TODO:
            - should val be used in some way?
    """
    new_val = random.randint(low, high)
    tries = 0
    while new_val == val:
        new_val = random.randint(low, high)
        tries += 1
        if tries == 10:
            return val + random.randint(low, high)
    return new_val


def generate_random_float(val, low=0, high=1.0):
    """ Generate a float between low and high
        Arguments:
            val (value): ignored for now

        Kwargs:
            low   (int): low value (default: 0)
            low   (int): high value (default: 1)
        Returns:
            float

        TODO:
            - should val be used in some way?

    """
    new_val = random.uniform(low, high)
    tries = 0
    while new_val == val:
        new_val = random.uniform(low, high)
        tries += 1
        if tries == 10:
            return val + random.uniform(low, high)
    return new_val


# NUMPY TRANSFORM

def numpy_type_transform(exc, dataset):
    """ Force a numpy type transformation when
        adding noise to numpy matrices. This will attempt to
        parse the objective type from the exception string
        and transform the array to that type.

        Arguments:
            exc                   (str): Exception string
            dataset (`dataset.DataSet`): dataset to transform

        Returns:
            None

        Note: this modifies types in place.
    """
    pattern = re.compile(r'could not convert (?P<type>\w+)')
    try:
        necessary_type = re.search(pattern, str(exc)).group('type')
    except AttributeError:
        logging.error('Error in numpy transform: %s', exc)
        return
    if necessary_type == 'float':
        dataset.records = dataset.records.astype(float)
    elif necessary_type == 'int':
        dataset.records = dataset.records.astype(int)
    elif necessary_type == 'string':
        dataset.records = dataset.records.astype(str)
