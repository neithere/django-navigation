# -*- coding: utf-8 -*-

""" Universal breadcrumbs navigation for Django.

FlatPages trail by:
jca <http://djangosnippets.org/snippets/519/>

Original idea and implementation of universal breadcrumbs for custom views by:
Thomas Guettler <http://groups.google.com/group/django-users/browse_thread/thread/f40f59e39cef59c4>

Unified templated breadcrumbs for both FlatPages and custom views support by:
Andy Mikhailenko <http://neithere.net>, <neithere@gmail.com>
"""

# TODO: tags instead of filters


# Python
from urlparse import urljoin

# Django
from django import template, http
from django.conf import settings
from django.core.urlresolvers import reverse, RegexURLResolver
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.http import urlquote
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string


# A list of site sections' URLs in desired order, i.e.:
#   NAVIGATION_SECTIONS = ('/about/', '/news/')
SECTIONS = getattr(settings, 'NAVIGATION_SECTIONS', ())

# Check if FlatPages middleware is connected and, if yes, auto-enable them
if 'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware' in settings.MIDDLEWARE_CLASSES:
    from django.contrib.flatpages.models import FlatPage
    ENABLE_FLATPAGES = True
else:
    ENABLE_FLATPAGES = False


register = template.Library()


class Crumb(object):
    """
    A navigation node.
    """

    def __init__(self, url, title, is_current=False, is_dummy=False):
        self.url        = url
        self.title      = title
        self.is_current = is_current
        self.is_dummy   = is_dummy

    def __unicode__(self):
        return unicode(self.title)


def _get_sections(request):
    """
    Returns list of sections (horizontal cut, base level).
    """

    sections = []
    for section_url in SECTIONS:
        crumb = find_crumb(section_url, request)
        if crumb:
            if section_url == '/':
                if request.path == section_url:
                    crumb.is_current = True
            else:
                if request.path.startswith(section_url):
                    crumb.is_current = True
            sections.append(crumb)

    return sections

def _get_trail(request, exclude_section=False):
    """
    Returns trail of breadcrumbs (vertical cut, excluding base level)
    """
    trail = []
    url = request.path
    while url:
        if url == '/':
            break
        if exclude_section and url in SECTIONS:
            break
        crumb = find_crumb(url, request)
        if not crumb:
            break
        trail.append(crumb)

        # go one level up
        url = urljoin(url, '..')

    trail.reverse()

    return trail

@register.filter
def get_title(request):
    return find_crumb(request.path, request)

@register.filter
def get_sections(request):
    return _get_sections(request)

@register.filter
def get_trail(request, exclude_section=False):
    return _get_trail(request, exclude_section)

@register.filter
def get_navigation(request):
    sections = _get_sections(request)
    trail = _get_trail(request, exclude_section=True)

    return mark_safe(render_to_string('navigation.html', dict(sections=sections,trail=trail)))

    """
    # defined in settings, crumbified here
    sections = (
        Crumb('/about/', u'О нас'),
        Crumb('/news/', u'Новости', is_current=True),
        Crumb('/users/', u'Персоналии'),
        )
    # depends on current path; generated here
    trail = (
        Crumb('/news/2008/', '2008'),
        Crumb('/foo/2008/08/', u'Август'),
        Crumb('/foo/2008/08/my-cool-article/', u'Моя статья'),
        )
    return mark_safe(render_to_string('navigation.html', pluck_locals('sections', 'trail')))
    #return mark_safe(unicode(' &rarr; '.join(breadcrumbs)))
    """

class CannotResolveCrumb(Exception):
    pass

def find_crumb(url, request):
    # by callback
    try:
        return find_crumb_by_callback(url, request)
    except CannotResolveCrumb, e:
        pass
    # by flatpage
    try:
        return find_crumb_by_flatpage(url)
    except CannotResolveCrumb, e:
        pass
    return Crumb(url, _('Undefined'), is_dummy=True)

def find_crumb_by_callback(url, request):
    """ Find a view function by urlconf; if the function has attribute 'navigation', use it. """
    callback = None
    urlconf  = getattr(request, "urlconf", settings.ROOT_URLCONF)
    resolver = RegexURLResolver(r'^/', urlconf)
    try:
        # Search for explicitly declared URLs
        callback, callback_args, callback_kwargs = resolver.resolve(url)
        bc = getattr(callback, 'navigation', None)
        if bc is None:
            raise CannotResolveCrumb, 'Callback %s.%s function "navigation" does not exist.' % (callback.__module__, callback.__name__)
        if isinstance(bc, basestring):
            title = bc
        else:
            if hasattr(bc, '__call__'):
                title = bc(request, *callback_args, **callback_kwargs)
            else:
                title = unicode(bc)    # handle i18n proxy objects
        return Crumb(url,title)
    except http.Http404, e:
        raise CannotResolveCrumb, e

def find_crumb_by_flatpage(url):
    if not ENABLE_FLATPAGES:
        raise CannotResolveCrumb, 'FlatPages are disabled'
    try:
        title = FlatPage.objects.get(url=url).title
        return Crumb(url,title)
    except FlatPage.DoesNotExist:
        raise CannotResolveCrumb
