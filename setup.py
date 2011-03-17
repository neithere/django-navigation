#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2008-2011 Andy Mikhailenko and contributors
#
#  This file is part of Django Navigation.
#
#  Django Navigation is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#
import os
from distutils.core import setup

from _version import version


readme = open(os.path.join(os.path.dirname(__file__), 'README')).read()

setup(
    # overview
    name         = 'django-navigation',
    description  = 'Extensible breadcrumbs navigation for Django.',
    long_description = readme,

    # technical info
    version      = version,
    packages     = ['navigation', 'navigation.templatetags'],
    requires     = ['django (>= 1.0)'],
    provides     = ['navigation'],

    # copyright
    author       = 'Andy Mikhailenko',
    author_email = 'andy@neithere.net',
    license      = 'GNU Lesser General Public License (LGPL), Version 3',

    # more info
    url          = 'http://bitbucket.org/neithere/django-navigation/',
    download_url = 'http://bitbucket.org/neithere/django-navigation/src/',

    # categorization
    keywords     = 'django breadcrumbs navigation',
    classifiers  = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Widget Sets',
    ],

    # release sanity check
    test_suite = 'nose.collector',
)
