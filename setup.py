#!/usr/bin/env python3

import sys
from codecs import open

from setuptools import setup

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 9)

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(
        """
==========================
Unsupported Python version
==========================
This version of Xython requires at least Python {}.{}, but
you're trying to install it on Python {}.{}. To resolve this,
consider upgrading to a supported Python version.

""".format(
            *(REQUIRED_PYTHON + CURRENT_PYTHON)
        )
    )
    sys.exit(1)

requires = []

test_requirements = [
    "pytest>=3",
]

setup(
    name="munin-node-python",
    version="0.1",
    description="Rewrite in python of munin-node",
    author="Corentin Labbe",
    author_email="clabbe.montjoie@gmail.com",
    url="https://github.com/montjoie/munin-node-python",
    packages=["munin-node-python"],
    package_data={"": ["LICENSE"]},
    package_dir={"munin-node-python": "munin-node-python"},
    entry_points={
        'console_scripts': [
            "munin-node = muninnodepython:main",
        ],
    },
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: System :: Monitoring",
    ],
    tests_require=test_requirements,
)
