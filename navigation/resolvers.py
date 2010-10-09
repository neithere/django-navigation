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
            crumb.is_current = bool(url == request.path)
            return crumb

    # TODO return None instead of a fake breadcrumb object
    # (this will be a backwards-incompatible change)
    # OTOH, maybe we still need this to store the partial URL?
    return Crumb(url, u'???', is_dummy=True)

def _resolve_url(url, request=None):
    urlconf  = getattr(request, "urlconf", settings.ROOT_URLCONF)
    urlresolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
    return urlresolver.resolve(url)

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
    try:
        callback, args, kwargs = _resolve_url(url, request)
    except urlresolvers.Resolver404:
        return None

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
