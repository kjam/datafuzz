==========================
Frequently Asked Questions
==========================

1. Why would I want to mess up my dataset?

    ``datafuzz`` is not to be used for every data science problem, but there are several where adding noise, nulls, fuzz or duplication can help you test and determine the resiliency of your model, pipeline or data processing script. It is built with these use cases in mind, so you can break your code before someone does it (intenionally or otherwise).

2. Why not use ``Hypothesis``?

    Why use just one? ``Hypothesis`` is a great tool, which I recommend for all data scientists for property-based testing. But hypothesis is not a tool for adding noise to an already compiled (or synthetically compiled dataset). Hypothesis can be used to generate a series of property-defined examples for your pipeline or use case; however, if you want to test for unexpected types or for realistic looking noise using your already defined dataset, it becomes difficult and cumbersome. This is one
    of the reasons I originally built ``datafuzz``. For this reason, I think it is useful to have more than one tool for your data science testing needs.

3. Why doesn't ``datafuzz`` have X feature?

    It's likely I didn't think it should be included in the initial scope. That said, I am all for determining good future features and welcome well-described and simple requests (as well as pull requests!). Head on over to the GitHub Issues to see if the feature is already in the works or open a new Issue to start the conversation. For more details on contributing, see the contributing guide.

4. What is fuzzing? Why use it in data science?

    Fuzz testing tests bad or malicious inputs and determines if the program crashes or raises errors. It is often used in the security community to investigate potential risks like buffer or stack overflows. Why use fuzzing for data science? Like software, data science code is often exposed to user input or outside APIs. Because of this, it is vulnerable to some of the same issues and attacks seen in web services. Even if the attacks or bad data are not malicious
    or are created by a bug in an internal system, we should test how the data science application, code or model behaves when given corrupt, noisy or duplicate data. Even if the expected behavior is a crash, we should know and test that in advance. This also helps determine if your extraction (ETL) or processing code (pipelines and workflows) address the issues or raise warnings when they see unexpected values.


