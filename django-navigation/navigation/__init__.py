# -*- coding: utf-8 -*-
#
#  Copyright (c) 2008 Andy Mikhailenko and contributors
#
#  Django Navigation is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#

" A breadcrumbs navigation application for Django framework. "

VERSION = (0, 1, 'alpha')

def get_version():
    " Returns the version as a human-format string. "
    v = '.'.join([str(i) for i in VERSION[:-1]])
    return '%s-%s' % (v, VERSION[-1])

__author__  = 'Andy Mikhailenko'
__license__ = 'GNU Lesser General Public License (GPL), Version 3'
__url__     = 'http://bitbucket.org/neithere/django-navigation/'
__version__ = get_version()
