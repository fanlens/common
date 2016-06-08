#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""package used for basics and db related access of the fanlens project"""

from setuptools import setup, find_packages

setup(
    name="fl-base",
    version="0.1",
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'sqlalchemy',
        'psycopg2'
    ],
)
