#!/usr/bin/env python

from setuptools import setup

setup(
    name='tap-appsflyer',
    version='0.0.15',
    description='Singer.io tap for extracting data from the AppsFlyer API',
    author='Atif8Ted',
    url='https://github.com/Atif8Ted/tap-appsflyer',
    classifiers=['Programming Language :: Python :: 3 :: Only'],
    py_modules=['tap_appsflyer'],
    install_requires=[
        'attrs==20.3',
        'singer-python==5.9.1',
        'requests==2.25',
        'backoff==1.8',
    ],
    extras_require={
        'dev': [
            'bottle',
            'faker'
        ]
    },
    entry_points={
        'console_scripts': [
            'tap-appsflyer=tap_appsflyer:main'
        ]
    },
    packages=['tap_appsflyer'],
    package_data={
        'tap_appsflyer': [
            'schemas/*.json']
    },
    include_package_data=True,
)
