#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

#with open('README.md') as readme_file:
#    readme = readme_file.read()

requirements = [
    'Click>=6.0',
    'confuse',
    'Pillow',
    'face-recognition'
]

setup(
    name='giface',
    version='0.1.0',
    description="GIF generator with face recognition",
#    long_description=readme,
    author="J0J0",
    author_email='jt@peek-a-boo.at',
    url='https://github.com/joj0/jekyll-helpers',
    packages=find_packages(include=['giface']),
    entry_points={
        # ATTENTION! ACHTUNG! ATENCIÓN!
        # 
        # The following lines determine what your CLI program is 
        # called and where it will look for it. Please edit to suit
        # your needs
        'console_scripts': [
            'giface=giface:cli'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='giface',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
