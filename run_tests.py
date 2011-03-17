#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management import call_command


settings.configure(
    INSTALLED_APPS = (
        'navigation',
        'django_coverage',
        'django.contrib.flatpages',
    ),
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    ROOT_URLCONF = '',
    COVERAGE_REPORT_HTML_OUTPUT_DIR = 'cover',
    NAVIGATION_URL_MAP = {
        '/mapped/url/string/': 'string mapped by url',
        '/mapped/url/callable/': lambda request: 'callable mapped by url',
    },
    NAVIGATION_NAME_MAP = {
        'mapped-name-string': 'string mapped by name',
        'mapped-name-callable': lambda request: 'callable mapped by name',
    },
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    ),
)

if __name__ == "__main__":
    call_command('test_coverage', 'navigation')
