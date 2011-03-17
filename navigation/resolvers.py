# -*- coding: utf-8 -*-

# Django
from django import http
from django.conf import settings
from django.core import urlresolvers

# this app
from helpers import Crumb


RESOLVERS = []


#-- URL to name resolver based on:
# http://djangosnippets.org/snippets/1378/ - by UloPe
# http://pastebin.com/7KfALc0j - by Fahrzin Hemmati
# This version also supports nested resolvers.
#
def _pattern_resolve_to_name(self, path):
    match = self.regex.search(path)
    if match:
        if self.name:
            return self.name
        elif hasattr(self, '_callback_str'):
            return self._callback_str
        elif self.callback:
            return "%s.%s" % (self.callback.__module__, self.callback.func_name)
        return ''

def _resolver_resolve_to_name(self, path):
    tried = []
    match = self.regex.search(path)
    if match:
        new_path = path[match.end():]
        for pattern in self.url_patterns:
            if isinstance(pattern, urlresolvers.RegexURLPattern):
                func = _pattern_resolve_to_name
            else:
                func = _resolver_resolve_to_name

            try:
                name = func(pattern, new_path)
            except urlresolvers.Resolver404, e:
                tried.extend([(pattern.regex.pattern + '   ' + t) for t in e.args[0]['tried']])
            else:
                if name:
                    return name
                tried.append(pattern.regex.pattern)

        raise urlresolvers.Resolver404, {'tried': tried, 'path': new_path}

def resolve_url_to_name(path, urlconf=None):
    #return get_resolver(urlconf).resolve_to_name(path)
    r = urlresolvers.get_resolver(urlconf)
    if isinstance(r, urlresolvers.RegexURLPattern):
        return _pattern_resolve_to_name(r, path)
    else:
        return _resolver_resolve_to_name(r, path)
#
#
#--- end


def crumb_resolver(f):
    """
    Decorator: registers given function as breadcrumb resolver. The function
    must accept Request object and URL string. (Note that the URL may not be
    equal to `request.path`.)
    """
    RESOLVERS.append(f)
    return f

def find_crumb(request, url=None, urlconf=None):
    url = url or request.path
    for resolver in RESOLVERS:
        crumb = resolver(request, url, urlconf=urlconf)
        if crumb is not None:
            crumb.is_current = request.path == url
            crumb.is_active  = request.path.startswith(url)
            return crumb

    # TODO return None instead of a fake breadcrumb object
    # (this will be a backwards-incompatible change)
    # OTOH, maybe we still need this to store the partial URL?
    return Crumb(url, u'???', is_dummy=True)

def _resolve_url(url, request=None, urlconf=None):
    urlconf = urlconf or getattr(request, "urlconf", settings.ROOT_URLCONF)
    urlresolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
    return urlresolver.resolve(url)

@crumb_resolver
def _resolve_by_settings_urls(request, url, urlconf=None):
    """
    Finds appropriate URL in settings dictionary ``NAVIGATION_URL_MAP`` and
    returns the Crumb object based on the value. The values can be strings or
    functions (or any callables). The functions are called as views. The
    callable values do not require that an existing endpoint and always get
    only one argument: the ``request`` object.
    """
    mapping = getattr(settings, 'NAVIGATION_URL_MAP', {})
    title = mapping.get(url, None)
    if title is not None:
        if hasattr(title, '__call__'):
            title = title(request)
#            try:
#                endpoint, args, kwargs = _resolve_url(url, request,
#                                                      urlconf=urlconf)
#            except urlresolvers.Resolver404:
#                # call at least somehow
#                title = title(request)#, *args, **kwargs)
#            else:
#                # call with full params
#                title = title(request, *args, **kwargs)
        return Crumb(url, title)

@crumb_resolver
def _resolve_by_settings_names(request, url, urlconf=None):
    mapping = getattr(settings, 'NAVIGATION_NAME_MAP', {})

    try:
        name = resolve_url_to_name(url, urlconf=urlconf)
    except urlresolvers.Resolver404:
        return None
    else:
        title = mapping.get(name, None)
        if title is not None:
            if hasattr(title, '__call__'):
                title = title(request)
            return Crumb(url, title)


@crumb_resolver
def _resolve_flatpage(request, url, urlconf=None):
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
def _resolve_by_callback(request, url, urlconf=None):
    """
    Finds a view function by urlconf. If the function has attribute
    'navigation', it is used as breadcrumb title. Such title can be either a
    callable or an object with `__unicode__` attribute. If it is callable, it
    must follow the views API (i.e. the only required argument is request
    object). It is also expected to return a `unicode` value.
    """
    try:
        callback, args, kwargs = _resolve_url(url, request, urlconf=urlconf)
    except urlresolvers.Resolver404:
        return None

    bc = getattr(callback, 'breadcrumb', None)
    if bc is None:
        bc = getattr(callback, 'navigation', None)
        if bc is not None:  # pragma: nocover
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
