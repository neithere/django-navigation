# -*- coding: utf-8 -*-
#
#  Copyright (c) 2008-2009 Andy Mikhailenko and contributors
#
#  Django Navigation is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#

def breadcrumb(crumb):
    """
    Usage::

        from navigation.decorators import breadcrumb

        @breadcrumb('greeting')
        def some_view(request):
            return 'Hello world!'

        @breadcrumb(lambda request: 'greeting for %s' % request.user.username)
        def some_view(request):
            return 'Hello %s!' % request.user.username
    """
    def wrapper(view):
        def inner(request, *args, **kwargs):
            return view(request, *args, **kwargs)
        inner.__dict__ = dict(view.__dict__, breadcrumb=crumb)
        inner.__name__ = view.__name__
        return inner
    return wrapper
