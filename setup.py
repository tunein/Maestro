""" Setup script for PyPI """
import os
from setuptools import setup
try:
    from ConfigParser import SafeConfigParser
except ImportError:
    from configparser import SafeConfigParser

setup(
    name='maestro',
    version='0.1.3',
    license='Apache License, Version 2.0',
    description='AWS Lambda tool for creating, updating, deleting, and publishing Lambdas',
    author="Max Moon, Perilune Industries",
    author_email='moon.maxwell@gmail.com',
    keywords="aws amazon web services lambda",
    platforms=['Any'],
    packages=['maestro'],
    entry_points = {
        'console_scripts': [
            'maestro=maestro.maestro:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)