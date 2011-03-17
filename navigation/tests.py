#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
from django.core.handlers.base import BaseHandler
from django.test import TestCase
from django.test.client import RequestFactory

from navigation import resolvers
from navigation.decorators import breadcrumb
from navigation.templatetags import navigation_tags


DEFAULT_RESPONSE = 'test_resp_123'


class LazyUnicode(object):
    def __init__(self, value):
        self.value = value
    def __unicode__(self):
        return unicode(self.value)

_ = LazyUnicode


#-- Views

def view_untitled(request):
    return DEFAULT_RESPONSE

def view_with_string_attribute(request):
    return DEFAULT_RESPONSE
view_with_string_attribute.breadcrumb = 'String'

def view_with_lazy_string_attribute(request):
    return DEFAULT_RESPONSE
view_with_lazy_string_attribute.breadcrumb = _('Lazy')

def view_with_callable_attribute(request):
    return DEFAULT_RESPONSE
view_with_callable_attribute.breadcrumb = lambda r: 'Callable'

@breadcrumb('Decorated')
def view_decorated(request):
    return DEFAULT_RESPONSE

#-- URL conf (see also test settings)

urlpatterns = patterns('',
    url(r'^untitled/', view_untitled),
    url(r'^attr/string/', view_with_string_attribute),
    url(r'^attr/lazy/', view_with_lazy_string_attribute),
    url(r'^attr/callable/', view_with_callable_attribute),
    url(r'^deco/', view_decorated),
    url(r'^nested/', include(
        patterns('',
            url(r'string/', view_with_string_attribute, name='nested-str')
        )
    )),
    url(r'^mapped/name/string/', view_untitled, name='mapped-name-string'),
    url(r'^mapped/name/callable/', view_untitled, name='mapped-name-callable'),
)

#-- Tests

class NavigationTestCase(TestCase):
    urls = urlpatterns

    def setUp(self):
        self.request_factory = RequestFactory()

    def make_request(self, url, with_middleware=False):
        request = self.request_factory.get(url)

        # see comments at http://djangosnippets.org/snippets/963/
        if with_middleware:
            handler = BaseHandler()
            handler.load_middleware()
            for middleware_method in handler._request_middleware:
                if middleware_method(request):
                    raise Exception("Couldn't create request mock object - "
                                    "request middleware returned a response")

        return request

    def assertCrumb(self, url, expected_title, with_middleware=False):
        """Asserts that given URL can be resolved to a Crumb object which, in
        turn, will contain given title.
        """
        request = self.make_request(url, with_middleware=with_middleware)
        crumb = resolvers.find_crumb(request)
        title = unicode(crumb)
        self.assertEquals(title, expected_title)

    def assertView(self, url):
        """Asserts that given URL yields a view that returns the default test
        response.
        """
        request = self.request_factory.get(url)
        endpoint, args, kwargs = resolvers._resolve_url(url, request)
        response = endpoint(request, *args, **kwargs)
        self.assertEquals(response, DEFAULT_RESPONSE)

    def assertViewMissing(self, url):
        try:
            self.assertView(url)
        except resolvers.urlresolvers.Resolver404:
            pass
        else:
            raise AssertionError('view found, expected to be missing')


class BasicResolverTestCase(NavigationTestCase):

    def test_missing(self):
        self.assertCrumb('--missing--', '???')
        self.assertViewMissing('--missing--')

    def test_nested_missing(self):
        url = '/nested/--missing--/'
        self.assertCrumb(url, '???')
        self.assertViewMissing(url)


class CallbackResolverTestCase(NavigationTestCase):

    def test_untitled(self):
        url = '/untitled/'
        self.assertCrumb(url, '???')
        self.assertView(url)

    def test_attribute_string(self):
        self.assertCrumb('/attr/string/', 'String')

    def test_attribute_lazy_string(self):
        self.assertCrumb('/attr/lazy/', 'Lazy')

    def test_attribute_callable(self):
        self.assertCrumb('/attr/callable/', 'Callable')

    def test_decorator(self):
        url = '/deco/'
        self.assertCrumb(url, 'Decorated')
        self.assertView(url)

    def test_nested_discoverable(self):
        url = '/nested/string/'
        self.assertCrumb(url, 'String')
        self.assertView(url)


class FlatpageResolverTestCase(NavigationTestCase):
    # Test settings must include this middleware:
    # django.contrib.flatpages.middleware.FlatpageFallbackMiddleware

    fixtures = ['test_flatpages.json']

    def test_no_middleware(self):
        mw = settings.MIDDLEWARE_CLASSES
        settings.MIDDLEWARE_CLASSES = [x for x in mw if 'Flatpage' not in x]
        self.assertCrumb('/flatpages/test/', '???')
        settings.MIDDLEWARE_CLASSES = mw

    def test_page_missing(self):
        self.assertCrumb('--missing--', '???', with_middleware=True)

    def test_page_exists(self):
        self.assertCrumb('/flatpages/test/', 'Test Page', with_middleware=True)


class SettingsNamesResolverTestCase(NavigationTestCase):
    def test_string(self):
        url = '/mapped/name/string/'
        self.assertCrumb(url, 'string mapped by name')

    def test_callable(self):
        url = '/mapped/name/callable/'
        self.assertCrumb(url, 'callable mapped by name')

class SettingsUrlsResolverTestCase(NavigationTestCase):
    def test_string(self):
        url = '/mapped/url/string/'
        self.assertCrumb(url, 'string mapped by url')

    def test_callable(self):
        url = '/mapped/url/callable/'
        self.assertCrumb(url, 'callable mapped by url')
