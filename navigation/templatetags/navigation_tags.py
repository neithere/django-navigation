# -*- coding: utf-8 -*-
"""
Template tags and filters
=========================

Loading::

    {% load navigation_tags %}

"""

__all__ = (
    # tags:
    'named_crumb', 'crumb_link',
    'get_breadcrumb_sections', 'get_breadcrumb_trail',
    # outdated filters:
    'get_navigation',
)

# TODO: tags instead of filters


# python
from functools import wraps
from urlparse import urljoin

# django
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

# this app
from navigation.helpers import Crumb
from navigation.resolvers import find_crumb, _resolve_url


# A list of site sections' URLs in desired order, i.e.:
#   NAVIGATION_SECTIONS = ('/about/', '/news/')
SECTIONS = getattr(settings, 'NAVIGATION_SECTIONS', ())


register = template.Library()


#--- BEGIN modified http://djangosnippets.org/snippets/1839/
class TemplateNode(template.Node):
    def __init__(self, args, var_name, func):
        self.args = [template.Variable(arg) for arg in args]
        self.var_name = var_name
        self.func = func

    def render(self, context):
        value = self.func(context, *[item.resolve(context) for item in self.args])
        if self.var_name:
            context[self.var_name] = value
            return ''
        else:
            return value

def parse_tokens(tokens):
    items = tokens.contents.split(None)
    # {% tag_name arg1 arg2 arg3 as variable %}
    # {% tag_name arg1 arg2 arg3 %}
    tag_name = items[0]
    if 1 < len(items) and "as" == items[-2]:
        var_name = items[-1]
        args = items[1:-2]
    else:
        var_name = None
        args = items[1:]
    return (tag_name, args, var_name)

def make_tag(func):
    @wraps(func)
    def do_func(parser, tokens):
        tag_name, args, var_name = parse_tokens(tokens)
        return TemplateNode(args, var_name, func)
    return do_func

def register_tag(func):
    """ Usage::

        @register_tag
        def foo(...):
            ...

    Same as::

        def foo(...):
            ...
        register.tag('foo', make_tag(foo)

    """
    return register.tag(func.__name__, make_tag(func))
#--- END modified http://djangosnippets.org/snippets/1839/


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
def get_title(context):
    import warnings
    warnings.warn('Template filter "get_title" is deprecated. Use "breadcrumb"'
                  ' tag instead. See django-navigation documentation for'
                  ' details.', DeprecationWarning)
    return find_crumb(request)

@register.filter
def get_sections(request):
    import warnings
    warnings.warn('Template filter "get_sections" is deprecated. Use '
                  '"get_breadcrumb_sections" tag instead. See '
                  'django-navigation documentation for details.',
                  DeprecationWarning)

    return _get_sections(request)

@register_tag
def get_breadcrumb_sections(context):
    """
    Returns a list of :term:`sections`. Usage::

        {% get_breadcrumb_sections as sections %}
        {% for section in sections %}
            ...
        {% endfor %}

    """
    return _get_sections(context['request'])

@register.filter
def get_trail(request, exclude_section=False):
    import warnings
    warnings.warn('Template filter "get_trail" is deprecated. Use '
                  '"get_breadcrumb_trail" tag instead. See '
                  'django-navigation documentation for details.',
                  DeprecationWarning)

    return _get_trail(request, exclude_section)

@register_tag
def get_breadcrumb_trail(context):
    """ Returns the trail of :term:`breadcrumbs`. Each breadcrumb is
    represented by a :class:`navigation.helpers.Crumb` instance.
    """
    return _get_trail(request, exclude_section=False)

@register.filter
def get_navigation(request):
    """ Returns the rendered navigation block. Requires that the
    `navigation.html` template exists. Two context variables are passed to it:

    * sections (see :func:`get_breadcrumb_sections`)
    * trail (see :func:`get_breadcrumb_trail`)

    """
    sections = _get_sections(request)
    trail = _get_trail(request, exclude_section=True)

    return mark_safe(render_to_string('navigation.html',
                                      dict(sections=sections,trail=trail)))


@register_tag
def breadcrumb(context, url=None):
    """ Returns breadcrumb label for given URL. Usage::

        <a href="/projects/">{% breadcrumb "/projects/" %}</a>

    Or without the argument to display current page's title::

        <h1>{% breadcrumb %}</h1>

    """
    return find_crumb(context['request'], url)

@register_tag
def named_crumb(context, name, *args, **kwargs):
    """ Resolves given named URL and returns the relevant breadcrumb label (if
    available). Usage::

        <a href="{% url project-detail project.slug %}">
            {% named_crumb project-detail project.slug %}
        </a>

    """
    url = reverse(name, args=args, kwargs=kwargs)
    return find_crumb(context['request'], url)

@register_tag
def crumb_link(context, name, *args, **kwargs):
    """ Acts like :func:`named_crumb` but also wraps the result into a
    link tag. Usage::

        <ul>
            <li>{% crumb_link 'auth_login' %}</li>
            <li>{% crumb_link 'project-index' %}</li>
        </ul>

    The result::

        <ul>
            <li><a href="/accounts/login/">Log in</a></li>
            <li><a href="/projects/">Projects</a></li>
        </ul>

    Please note that you have to use quotes, otherwise the arguments are
    considered variable names.
    """
    url = reverse(name, args=args, kwargs=kwargs)
    label = find_crumb(context['request'], url)
    return u'<a href="%s">%s</a>' % (url, label)
