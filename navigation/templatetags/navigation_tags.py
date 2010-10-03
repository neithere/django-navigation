# -*- coding: utf-8 -*-
"""
Template tags and filters
=========================

Loading::

    {% load navigation_tags %}

"""

__all__ = ['get_sections', 'get_trail', 'get_navigation']

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
    """ Returns current page's title. """
    return find_crumb(request)

@register.filter
def get_sections(request):
    """ Returns a list of :term:`sections`. """
    return _get_sections(request)

@register.filter
def get_trail(request, exclude_section=False):
    """ Returns the trail of :term:`breadcrumbs`. Each breadcrumb is
    represented by a :class:`navigation.helpers.Crumb` instance.
    """
    return _get_trail(request, exclude_section)

@register.filter
def get_navigation(request):
    """ Returns the rendered navigation block. Requires that the
    `navigation.html` template exists. Two context variables are passed to it:

    * sections (see :func:`get_sections`)
    * trail (see :func:`get_trail`)

    """
    sections = _get_sections(request)
    trail = _get_trail(request, exclude_section=True)

    return mark_safe(render_to_string('navigation.html', dict(sections=sections,trail=trail)))
