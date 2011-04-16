# -*- coding: utf-8 -*-
#
#  Copyright (c) 2008-2009 Andy Mikhailenko and contributors
#
#  Django Navigation is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#
"""
Decorators
==========
"""
from functools import wraps

__all__ = ['breadcrumb']


def breadcrumb(crumb, coerce_to=None):
    """
    Usage::

        from navigation.decorators import breadcrumb

        @breadcrumb('greeting')
        def some_view(request):
            return 'Hello world!'

        @breadcrumb(lambda request: u'greeting for %s' % request.user.username)
        def some_view(request):
            return 'Hello %s!' % request.user.username

    .. note::

        By default the value returned by a callable is required to be a
        ``unicode`` object. If the function returns a model instance, its
        ``__unicode__`` method is *not* called. Use ``coerce_to=unicode``.

    :param crumb:

        A ``unicode`` string or a callable that returns it.

    :param coerce_to:

        Coerces *crumb* to given type. The value can be ``unicode`` or any
        callable that returns a ``unicode`` object.

    """
    def wrapper(view):
        @wraps(view)
        def inner(request, *args, **kwargs):
            return view(request, *args, **kwargs)

        if coerce_to is not None:
            inner.breadcrumb = (
                lambda *args, **kwargs: coerce_to(crumb(*args, **kwargs)))
        else:
            inner.breadcrumb = crumb
        return inner
    return wrapper
