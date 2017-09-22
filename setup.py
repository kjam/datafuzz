#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Datafuzz setup script for proper installation and setup"""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'faker',
    'dataset',
    'pyyaml',
]

setup_requirements = [
]

test_requirements = [
    'numpy',
    'pandas',
    'pytest',
    'pytest-coverage',
    'pylint',
]

setup(
    name='datafuzz',
    version='0.1.0-alpha',
    description="A data-science library built for testing cleaning, schema validation and model robustness. It messes up your data so you can test your data engineering and data science code (before it breaks in production).",
    long_description=readme + '\n\n' + history,
    author="Katharine Jarmul",
    author_email='katharine@kjamistan.com',
    url='https://github.com/kjam/datafuzz',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'datafuzz=datafuzz.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='datafuzz',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
