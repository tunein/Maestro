""" Setup script for PyPI """
import os
from setuptools import setup
try:
    from ConfigParser import SafeConfigParser
except ImportError:
    from configparser import SafeConfigParser

setup(
    name='maestro',
    version='0.1.6',
    license='Apache License, Version 2.0',
    description='AWS Lambda tool for creating, updating, deleting, and publishing Lambdas',
    author="Max Moon, Perilune Industries",
    author_email='moon.maxwell@gmail.com',
    keywords="aws amazon web services lambda",
    platforms=['Any'],
    packages=['maestro', 'maestro.actions', 'maestro.config', 'maestro.helpers', 'maestro.providers', 'maestro.providers.aws'],
    entry_points = {
        'console_scripts': [
            'maestro=maestro.main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)