#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2008-2009 Andy Mikhailenko and contributors
#
#  This file is part of Django Navigation.
#
#  Django Navigation is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#

" Django Navigation setup "

from setuptools import setup, find_packages
from navigation import __version__

setup(
    name         = 'django-navigation',
    version      = __version__,
    packages     = find_packages(exclude=['example']),

    install_requires = ['django >= 1.0'],

    description  = 'A breadcrumbs navigation application for Django framework.',
    author       = 'Andy Mikhailenko',
    author_email = 'andy@neithere.net',
    url          = 'http://bitbucket.org/neithere/django-navigation/',
    download_url = 'http://bitbucket.org/neithere/django-navigation/src/',
    license      = 'GNU Lesser General Public License (LGPL), Version 3',
    keywords     = 'django breadcrumbs navigation',
    classifiers  = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Widget Sets',
    ],
)
