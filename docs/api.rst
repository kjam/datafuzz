.. _api:

Developer Interface
===================

.. module:: datafuzz

Here are the main interfaces of datafuzz for general use.


Dataset class
-------------

.. autoclass:: datafuzz.DataSet
    :members:

Strategy classes
----------------

.. autoclass:: datafuzz.strategy.Strategy
    :members:
.. autoclass:: datafuzz.duplicator.Duplicator
    :members:
.. autoclass:: datafuzz.fuzz.Fuzzer
    :members:
.. autoclass:: datafuzz.noise.NoiseMaker
    :members:

Parser classes
---------------

.. autoclass:: datafuzz.parsers.StrategyYAMLParser
    :members:
.. autoclass:: datafuzz.parsers.StrategyCLIParser
    :members:
.. autoclass:: datafuzz.parsers.SchemaYAMLParser
    :members:
.. autoclass:: datafuzz.parsers.SchemaCLIParser
    :members:

Output classes
--------------

.. autoclass:: datafuzz.output.CSVOutput
    :members:
.. autoclass:: datafuzz.output.JSONOutput
    :members:
.. autoclass:: datafuzz.output.SQLOutput
    :members:
.. autofunction:: datafuzz.output.obj_to_output

Generator classes
-----------------

.. autoclass:: datafuzz.generators.DatasetGenerator
    :members:


For more use cases, please reference the :doc:`usage` section.
