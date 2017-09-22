=============
Quickstart
=============

Want to get started right away? Here is a five minute or less tutorial on using ``datafuzz``.

Defining YAML Strategies
-------------------------

One of the easiest ways to get started using ``datafuzz`` is to define strategies in YAML format given a dataset you already have. Let's take a look at an example YAML file:

    .. literalinclude:: ../datafuzz/examples/yaml_files/read_csv_and_dupe.yaml

In this file, you set up the data ``input`` and ``output``, which are both CSVs. Then, you apply strategies, which is only one item in this case. This calls for duplication of records using 10% of rows and adds random noise to those duplicate rows.

We can now run these transformations from the command line.

.. code-block:: bash
    
    $ datafuzz run datafuzz/examples/read_csv_and_dupe.yaml

When complete, we can check the difference in number of lines for the files.

.. code-block:: bash
    
    $ wc -l datafuzz/examples/data/sales_data*
      
    2001 datafuzz/examples/data/sales_data.csv
    2201 datafuzz/examples/data/sales_data_with_dupes.csv
    4202 total


That's it! For more information on all available strategies, check out :doc:`strategies`. 

Generation and Noise in Jupyter
-------------------------------

Are you using Jupyter notebooks for your development? `datafuzz` can easily integrate with your workflow. 

To get started, take a look at `the example notebooks in the repository <https://github.com/kjam/datafuzz/tree/master/examples/notebooks>`_.


Generating Synthetic Data
-------------------------

Generating synthetic data to use is easy as Py with ``datafuzz``. An easy schema definition can be declared using simple YAML:

    .. literalinclude:: ../datafuzz/examples/yaml_files/iot_schema.yaml

This file declares some useful schema, such as the number of rows to generate (``num_rows``), timeseries information (which is only required if you want a timeseries to be generated) and the schema for each row. You can use ranges, aranges, lists or faker providers (see `faker provider documentations <http://faker.readthedocs.io/en/master/providers.html>`_).

To generate the data, you can run the command line:

.. code-block:: bash

    $ datafuzz generate datafuzz/examples/yaml_files/iot_schema.yaml

To see our generated data, we can peek at the output file:

.. code-block:: bash

    $ head -n 5 /tmp/iot.csv

    build,temperature,username,heartrate,latest,note
    59803106-7fa4-5fe3-2ad8-0e962c4e5666,13,rramirez,86,0,n/a
    d865fbc7-d43a-e001-ea67-d1892c26aa41,26,kristi42,72,0,n/a
    535f4f08-ca2b-c418-081b-bc8e572087e9,7,jacksonterri,88,1,n/a
    69e2796f-f2a2-f139-1b06-cbc500cb387b,6,eerickson,75,0,wake
