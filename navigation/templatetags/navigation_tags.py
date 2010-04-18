# -*- coding: utf-8 -*-

"""
Universal breadcrumbs navigation for Django.

FlatPages trail by:
jca <http://djangosnippets.org/snippets/519/>

Original idea and implementation of universal breadcrumbs for custom views by:
Thomas Guettler <http://groups.google.com/group/django-users/browse_thread/thread/f40f59e39cef59c4>

Unified extensible templated breadcrumbs for both FlatPages and custom views by:
Andrey Mikhaylenko <http://neithere.net>, <andy@neithere.net>
"""

# TODO: tags instead of filters


# python
from urlparse import urljoin

# django
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

# this app
from navigation.helpers import Crumb
from navigation.resolvers import find_crumb


# A list of site sections' URLs in desired order, i.e.:
#   NAVIGATION_SECTIONS = ('/about/', '/news/')
SECTIONS = getattr(settings, 'NAVIGATION_SECTIONS', ())


register = template.Library()

def _get_sections(request):
    """
    Returns list of sections (horizontal cut, base level).
    """

    sections = []
    for section_url in SECTIONS:
        crumb = find_crumb(request, section_url)
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
        crumb = find_crumb(request, url)
        if not crumb:
            break
        trail.append(crumb)

        # go one level up
        url = urljoin(url, '..')

    trail.reverse()

    return trail

@register.filter
def get_title(request):
    return find_crumb(request)

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
