===========
I/O Options
===========

Whether you are using a generator or a strategy, you will want to define inputs and outputs for your data. These are standard across ``datafuzz`` as they are defined in the ``DataSet`` class. The current supported data types for a dataset are:

- lists
- numpy 2D arrays
- pandas dataframes

``datafuzz`` will utilize pandas dataframes internally to represent and modify the records if you have pandas installed. If you want to avoid this, you may pass ``pandas=False`` in your initialization of your ``DataSet`` object.

Input options
-------------

You can read in several additional data formats, which will be used to create a ``DataSet`` object. These are normally defined in the Parser object, or are passed in the ``DataSet`` object itself. Options are as follows:

    files:
        defined by specifying ``file://$PATH_AND_FILENAME``. Currently, only CSV and JSON files are supported.

    sql queries:
        defined by passing ``'sql'`` as input. You must then also pass optional arguments for your parser (``db_uri`` and ``query``)

Output options
--------------

Output can be generated from every ``DataSet`` object by calling the ``to_output`` method, which will return either the output string or the output object. It will return a string for non-Python objects (such as sql tables and files) and an object for all native objects.

For output, you can define the following options:

    files:
        defined by specifying ``file://$PATH_AND_FILENAME``. Currently, only CSV and JSON files are supported.

    sql table:
        defined by passing ``'sql'`` as output. You must then also pass optional arguments for your output (``db_uri`` and ``table``)

    pandas dataframe:
        defined by passing ``'pandas'``

    numpy 2D array:
        defined by passing ``'numpy'``

    list:
        defined by passing ``'list'``


If you are interested in an example of using ``datafuzz`` as a stream, please see the streaming example in the `example directory <https://github.com/kjam/datafuzz/tree/master/datafuzz/examples>`_.

