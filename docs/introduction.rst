Motivation
----------

The goal of ``datafuzz`` is to give you the ability to test your data science code and models with BAD data. Why?? Because sometimes your code will see bad data, especially if you are running it in production. ``datafuzz`` is motivated by the idea that testing data pipelines, data science code and production-facing models should involve some elements of fuzzing -- or introducing bad and random data to determine possible security and crash risks.


Features
---------

* Transform your data by adding noise to a subset of your rows
* Duplicate data to test your duplication handling
* Generate synthetic data for use in your testing suite
* Insert random "dumb" fuzzing strategies to see how your tools cope with bad data
* Seamlessly handle normal input and output types including CSVs, JSON, SQL, numpy and pandas
