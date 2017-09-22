==========
Generators
==========

Currently, there is only one generator ``DatasetGenerator`` which allows you to define schema for new datasets. This generator requires use of the ```faker`` library <http://faker.readthedocs.io/>`_. 

Generator Initialization Requirements
-------------------------------------

To initialize a generator you need the following:

    parser:
        a ``parsers.SchemaYAMLParser`` or ``parsers.SchemaCLIParser`` or a dictionary with the appropriate keys (see Required Parser Arguments below)

    output:
        a string specifying output (see: :doc:`io_options`)


Required Parser Arguments
-------------------------

The ``SchemaYAMLParser`` and ``SchemaCLIParser`` as well as any dictionary you use in leiu of a parser object need to have certain keys in order to generate the data. The required arguments are as follows:

    schema:
        a dictionary of column names and values to use. Optional values are any of the `faker providers <http://faker.readthedocs.io/en/master/providers.html>`_ defined like ``'faker.name'``, as well as lists or iterators of options or ``range`` and ``arange`` objects.

    num_rows:
        an integer for the number of rows to generate

The parser objects (or a dictionary you use) may also have the following optional arguments which are used to create timeseries:

    start_time:
        isoformat start time which will be used to generate a timeseries. Currently, the timeseries column defaults to 'timestamp'.

    end_time:
        if desired, set an end_time in isoformat. Note: this may or may not be reached given the number of rows requirement.

    increments:
        choice from: 'days', 'hours', 'seconds' and 'random' for timestamp increments. Default is random which is a mix of days, hours and seconds.

For more examples on how to utilize these generators, check the :doc:`usage` documentation.
