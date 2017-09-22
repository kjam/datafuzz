===========
Strategies
===========

In ``datafuzz``, strategies are used to define ways to fuzz or add noise to data. There are currently three types of strategies which reflect three different classes: ``Duplicator``, ``NoiseMaker`` and ``Fuzzer``. 


Required Initialization Values
------------------------------

To use each strategy, you must define certain attributes, as follows.

For **all strategies**, you need to define:

    dataset:
        a ``datafuzz.DataSet`` object to apply the strategy to

    percentage:
        percentage of rows to fuzz, noise or duplicate (0-100)


The ``NoiseMaker`` class has some additional requirements:

    columns:
        a list of columns to apply the noise to (this will be chosen at random if not provided)

    noise:
        a list of possible noise to apply. Options are:

            - 'add_nulls': add null values
            - 'string_permutation': apply string transformations
            - 'random': generate some random values based on col type
            - 'range': change values into given or column range
            - 'type_transform': apply type transformations


The ``Fuzzer`` class has one additional requirements:

    columns:
        a list of columns to apply the fuzz to (this will be chosen at random if not provided)


The ``Duplicator`` class has one additional options:

    add_noise:
        boolean to signify if random noise should be applied to the duplicated rows


Running the strategy
--------------------

For each strategy class, you can run the strategy using ``self.run_strategy``. This will apply the transformation directly to the dataset records.
