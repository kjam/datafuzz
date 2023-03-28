========
datafuzz
========

.. image:: https://img.shields.io/pypi/v/datafuzz.svg
        :target: https://pypi.python.org/pypi/datafuzz

.. image:: https://img.shields.io/travis/kjam/datafuzz.svg
        :target: https://travis-ci.org/kjam/datafuzz

.. image:: https://readthedocs.org/projects/datafuzz/badge/?version=latest
        :target: https://datafuzz.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/kjam/datafuzz/shield.svg
     :target: https://pyup.io/repos/github/kjam/datafuzz/
     :alt: Updates


A data-science library built for testing cleaning, schema validation and model robustness. Datafuzz messes up your data so you can test things before they go wrong in production.

* Free software: BSD license
* Documentation: https://datafuzz.readthedocs.io.


Features
--------

* Transform your data by adding noise to a subset of your rows
* Duplicate data to test your duplication handling
* Generate synthetic data for use in your testing suite
* Insert random "dumb" fuzzing strategies to see how your tools cope with bad data
* Seamlessly handle normal input and output types including CSVs, JSON, SQL, numpy and pandas


Installation
------------

Install datafuzz by running::

    $ pip install datafuzz

Recommended use is with a proper Virtual Environment (learn more about `virtual environments <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`).

For more details see Installation Instructions.

Contribute
----------

- Issue Tracker: https://github.com/kjam/datafuzz/issues
- Source Code: https://github.com/kjam/datafuzz

Support
-------

If you are having issues, please let reach out via the Repository issues.

License
-------

The project is licensed under the BSD license.

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.



.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

