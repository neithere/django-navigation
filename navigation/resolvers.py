# -*- coding: utf-8 -*-

# Django
from django import http
from django.conf import settings
from django.core import urlresolvers

# this app
from helpers import Crumb


RESOLVERS = []

def crumb_resolver(f):
    """
    Decorator: registers given function as breadcrumb resolver. The function
    must accept Request object and URL string. (Note that the URL may not be
    equal to `request.path`.)
    """
    RESOLVERS.append(f)
    return f

def find_crumb(request, url=None):
    url = url or request.path
    for resolver in RESOLVERS:
        crumb = resolver(request, url)
        if crumb is not None:
            return crumb

    # TODO return None instead of a fake breadcrumb object
    # (this will be a backwards-incompatible change)
    # OTOH, maybe we still need this to store the partial URL?
    return Crumb(url, '???', is_dummy=True)

def _resolve_url(request, url):
    urlconf  = getattr(request, "urlconf", settings.ROOT_URLCONF)
    urlresolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
    return urlresolver.resolve(url)

@crumb_resolver
def _resolve_by_settings(request, url):
    """
    Finds appropriate URL in settings variable ``NAVIGATION_URL_MAP`` and
    processes
    """
    if not hasattr(settings, 'NAVIGATION_URL_MAP'):
        return None

    try:
        endpoint, args, kwargs = _resolve_url(request, url)
    except urlresolvers.Resolver404:
        return None

    print
    print '*** need a crumb for', endpoint, args, kwargs
    for name, crumb_func in settings.NAVIGATION_URL_MAP:
        if name == url:
            return crumb_func(request, *args, **kwargs)
            print 'muhaha'
        else:
            print name, url
        print '*** trying', name, args, kwargs
        try:
            print endpoint, 'vs', crumb_func, 'vs', args, kwargs
#            print '*** reversing', endpoint, args, kwargs
#            reversed_url = urlresolvers.reverse(name, args=args, kwargs=kwargs)
        except urlresolvers.NoReverseMatch:
            print '*** ...no reverse match.'
            continue
        else:
            print '*** matched'
#            if url == reversed_url:
#                print '*** MATCHED!'
#                return crumb_func(request, args, kwargs)
#            print '***', url, '!=', reversed_url
    return None

@crumb_resolver
def _resolve_flatpage(request, url):
    path = 'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'
    if path not in settings.MIDDLEWARE_CLASSES:
        return None

    from django.contrib.flatpages.models import FlatPage

    try:
        obj = FlatPage.objects.get(url=url)
    except FlatPage.DoesNotExist:
        return None
    else:
        return Crumb(url, obj.title)

@crumb_resolver
def _resolve_by_callback(request, url):
    """
    Finds a view function by urlconf. If the function has attribute
    'navigation', it is used as breadcrumb title. Such title can be either a
    callable or an object with `__unicode__` attribute. If it is callable, it
    must follow the views API (i.e. the only required argument is request
    object). It is also expected to return a `unicode` value.
    """
    callback, args, kwargs = _resolve_url(request, url)
    bc = getattr(callback, 'breadcrumb', None)
    if bc is None:
        bc = getattr(callback, 'navigation', None)
        if bc is not None:
            import warnings
            warnings.warn('The "navigation" attribute is deprecated, use '
                          '"breadcrumb" instead.')
    if bc is None:
        return None

    if hasattr(bc, '__call__'):
        # the breadcrumb is a function with an API identical to that of views.
        try:
            title = bc(request, *args, **kwargs)
        except http.Http404:
            return None
        assert isinstance(title, basestring), (
            'Breadcrumb function must return Unicode, not %s' % title)
    else:
        title = unicode(bc)    # handle i18n proxy objects

    return Crumb(url, title)
