#!/usr/bin/env python
from setuptools import setup, find_packages

NAME = 'lime-docs-theme'
URL = 'https://github.com/lundalogik/{}'.format(NAME)
DESCRIPTION = 'Theme for the crm-platform docs, based on sphinx_materialdesign_theme'
VERSION = '0.1.0'


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=readme(),
    url=URL,
    include_package_data=True,
    packages=find_packages(),
    command_options={
        'build_sphinx': {
            'project': ('setup.py', NAME),
            'version': ('setup.py', VERSION),
            'release': ('setup.py', VERSION),
        }
    },
    license= 'MIT License',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Software Development :: Documentation"
    ],
    install_requires=[
        # Add dependencies to other python packages here
    ],
    entry_points = {
        'sphinx.html_themes': [
            'sphinx_materialdesign_theme = sphinx_materialdesign_theme',
        ]
    }
)
