# -*- coding: utf-8 -*-
# pylint: disable=unused-import
""" Set HAS_NUMPY and HAS_PANDAS constants
    TODO: should versions be checked?
"""
import sys

try:
    import numpy as np
    import pandas as pd
except ImportError:
    pass

HAS_NUMPY = 'numpy' in sys.modules
HAS_PANDAS = 'pandas' in sys.modules
