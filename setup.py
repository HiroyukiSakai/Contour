#!/usr/bin/env python

from setuptools import setup

setup(
    name='Contour',
    version='0.0.1',
    description='Web-based drawing game',
    author='Hiroyuki Sakai',
    author_email='hiroyuki.sakai@alumni.tuwien.ac.at',
    url='http://contour-sakai.rhcloud.com/',
    install_requires=[
        'Django==1.6.1',
        'Pillow==2.3.0',
        'numpy==1.8.0',
        'scipy==0.13.2',
        'scikit-image==0.9.3'
    ],
)
