#!/usr/bin/env python
import os
from setuptools import setup, find_packages
import sys

extra_kwargs = {}
extra_kwargs['install_requires'] = ['six==1.10.0', 'termcolor==1.1.0']
if sys.version_info < (2, 7):
    extra_kwargs['install_requires'].append('argparse')


setup(name="glancespeed",
    packages=['glancespeed'],
    version="0.0.1",
    description="Nephila's internal tool to show Google PageSpeed Insights reports differences",
    license="MIT",
    author="Andrea Stagi",
    author_email="stagi.andrea@gmail.com",
    url="",
    keywords= "measure optimize website page size pagespeed insights reporting psi",
    entry_points = {
        'console_scripts': [
            'glancespeed = glancespeed.main:main',
        ],
    },
    zip_safe = False,
    **extra_kwargs)