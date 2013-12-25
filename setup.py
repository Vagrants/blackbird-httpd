#!/usr/bin/env python
# -*- codig: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='blackbird-httpd',
    version='0.1.0',
    description=(
        'get httpd stats by using server-status.'
    ),
    author='makocchi',
    author_email='makocchi@gmail.com',
    url='https://github.com/Vagrants/blackbird-httpd',
)
