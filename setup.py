#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

install_requirements = [
    "sceptre>=1.3.0"
]

test_requirements = [
    "pytest>=3.2",
    "troposphere>=2.0.0",
    "moto==0.4.31",
    "mock==2.0.0",
    "behave==1.2.5",
    "freezegun==0.3.9"
]

setup_requirements = [
    "pytest-runner>=3"
]

setup(
    name="sceptre_migration_tool",
    version="0.0.1",
    description="Migratioln Tool for Sceptre Cloud Provisioning Tool",
    long_description=readme + "\n\n" + history,
    author="Intuit",
    author_email="oazmon@intuit.com",
    license='Apache2',
    url="https://github.com/cloudreach/sceptre_migration_tool",
    packages=[
        "sceptre_migration_tool"
    ],
    package_dir={
        "sceptre_migration_tool": "sceptre_migration_tool"
    },
    py_modules=["sceptre_migration_tool"],
    entry_points="""
        [console_scripts]
        sceptre_migration_tool=sceptre_migration_tool.cli:cli
    """,
    data_files=[
    ],
    include_package_data=True,
    zip_safe=False,
    keywords="sceptre_migration_tool, sceptre, migration",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Environment :: Console",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ],
    test_suite="tests",
    install_requires=install_requirements,
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    extras_require={
        "test": test_requirements
    }
)
