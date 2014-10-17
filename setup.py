#!/usr/bin/env python

import os
import sys

if hasattr(os, 'link'):
    del os.link  # Hack workaround for http://bugs.python.org/issue8876

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

from pip.req import parse_requirements

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

# http://stackoverflow.com/questions/14399534/how-can-i-reference-requirements-txt-for-the-install-requires-kwarg-in-setuptool
install_reqs = parse_requirements('requirements.txt')
req_list = [str(ir.req) for ir in install_reqs]

readme = open('README.rst').read()
# doclink = """
# Documentation
# -------------
#
# The full documentation is at http://wabbit_wappa.rtfd.org."""
doclink = ''
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='wabbit_wappa',
    version='0.3.0',
    description='Wabbit Wappa is a full-featured Python wrapper for the Vowpal Wabbit machine learning utility.',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author="Michael J.T. O'Kelly",
    author_email='mokelly@gmail.com',
    url='https://github.com/mokelly/wabbit_wappa',
    packages=find_packages(exclude=['test*']),
    package_dir={'wabbit_wappa': 'wabbit_wappa'},
    include_package_data=True,
    install_requires=req_list,
    license='MIT',
    keywords='wabbit_wappa',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
