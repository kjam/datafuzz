=====================================
Using datafuzz with Python or Jupyter
=====================================

You don't need to use ``datafuzz`` with the CLI, you can also use it with your native Python scripts, frameworks or Jupyter notebooks. To see some Jupyter notebook integration examples, check out `the Jupyter Notebooks included in the examples directory <https://github.com/kjam/datafuzz/tree/master/datafuzz/examples/notebooks>`_.

For integration with your Python script, the necessary parameters for initialization may differ depending on the class you are using to transform your data.

To do so, you might start with a dataset in the shape of a Pandas DataFrame or a `numpy` matrix or even a Python list of dictionaries and list. You could also generate a new dataset by using the generator class.

Let's generate a simple timeseries using the generator:


.. code-block:: python

    from datafuzz.generators import DatasetGenerator

    generator = DatasetGenerator({
        'output': 'pandas',
        'schema': {
            'category': list('ABCD'),
            'model': range(4,8),
            'plate': 'faker.license_plate',
            'year': range(2001, 2018),
            'color': 'faker.safe_color_name',
            'price': range(20000, 50000, 1000)
        },
        'num_rows': 1000,
    })

    generator.generate()

    dataset = generator.to_output()

    print(dataset.head())

Your output should look something like this::

      category    color  model     plate  price  year
    0        A  fuchsia      4   0736 CF  20000  2003
    1        B     teal      6   EXS 036  29000  2004
    2        D     teal      6   1QX5388  32000  2009
    3        C     navy      5  6P 15774  30000  2011
    4        A    white      4   0SQ D88  31000  2013


Now we have a dataset that holds our generated dataframe. If instead we had imported or transformed the data into a dataframe, we can start at this step. 

Now that we have some data to work with, let's determine what transformation there are available. The strategies available are the following classes:

- Duplicator
- Fuzzer
- NoiseMaker

Let's use the ``NoiseMaker`` class to add some noise to our dataset.

.. code-block:: python

    from datafuzz import DataSet, NoiseMaker

    dataset = DataSet(dataset, 
                      output='file://my_new_file.json')

    noiser = NoiseMaker(
        dataset,
        noise=['add_nulls', 'random'],
        columns=['price', 'model', 'year'],
        percentage=30,
    )
    noiser.run_strategy()

At this point, your ``DataSet`` object is transformed. You can check it by looking at the 5 initial items in the dataset:

.. code-block:: python

    print(dataset[:5])

Your data should now be a *bit* messy::

  category    color     model     plate         price         year
  0        D   maroon  4.376930   179-IYJ  29000.000000  2006.000000
  1        D    green  4.000000  P 336983  15468.136372  1598.702067
  2        D     gray  5.270262   DIV-042  20000.000000  2002.000000
  3        C     aqua  2.017815   84R 707  38000.000000          NaN
  4        C  fuchsia  6.000000   8078 TU  37000.000000  1995.355014


You can continue running transformations, if you like:

.. code-block:: python

    from datafuzz import Duplicator

    duplicator = Duplicator(
        dataset,
        percentage=20,
    )
    duplicator.run_strategy()

When you are done with the transformations, you can export the data depending on the output you set when the dataset was first initiated. You can also set a new output string. Available outputs are as follows:

- pandas dataframe: 'pandas'
- numpy 2D array: 'numpy'
- ``datafuzz.DataSet``: 'dataset'
- list: 'list'
- CSV files: 'file://foo.csv'
- JSON files: 'file://foo.json'
- SQL: 'sql'

If you use the 'sql' output, you need to also set a value for ``'table'`` and for ``'db_uri'``. For an in-depth treatment of input and output options, please see :doc:`io_options`.

To then get the output, you need to run ``to_output``:

.. code-block:: python

    output = dataset.to_output()

    print(output)


And now to check the file::

    head -c 200 my_new_file.csv

    {"0":{"category":"D","color":"maroon","model":2.5774000851,"plate":"0ME 062","price":null,"year":2008.0},"1":{"category":"C","color":"black","model":null,"plate":"UGV-266","price":39000.0,"year":2010.


That covers the vast majority of the functionality contained within `datafuzz`. Want to see more features? Check the backlog and feel free to follow steps for contributing!
