#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2008 Andy Mikhailenko and contributors
#
#  This file is part of Django Navigation.
#
#  Django Navigation is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#

" Django Navigation setup "

from distutils.core import setup
from navigation import get_version

setup(
    name         = 'Django Navigation',
    version      = get_version(),
    description  = 'A breadcrumbs navigation application for Django framework.',
    author       = 'Andy Mikhailenko',
    author_email = 'andy@neithere.net',
    url          = 'http://bitbucket.org/neithere/django-navigation/',
    download_url = 'http://bitbucket.org/neithere/django-navigation/src/',
    license      = 'GNU Lesser General Public License (LGPL), Version 3',
    packages     = ['navigation'],
)
