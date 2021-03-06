Overview
========

Let's assume we have this URL path::

    /news/2010/oct/hello-world/

We need to convert it to :term:`breadcrumbs` and display along the heading this
way::

    News → 2010 news → October 2010

So we just type this in our template::

    {% get_breadcrumb_trail as trail %}
    <ul>
    {% for crumb in trail %}
        <li><a href="{{ crumb.url }}">{{ crumb }}</a></li>
    {% endfor %}
    </ul>
    <h1>{% breadcrumb %}</h1>

...and this is the result::

    <ul>
        <li><a href="/news/>News</li>
        <li><a href="/news/2010/">2010 news</li>
        <li><a href="/news/2010/oct/">October 2010</a></li>
    </ul>
    <h1>Hello world</h1>

How does this work?
-------------------

Current URL path is split into hierarchical parts::

    * /news/
    * /news/2010/
    * /news/2010/oct/
    * /news/2010/oct/hello-world/

For each part a :class:`navigation.helpers.Crumb` instance is created. It
stores the URL and the corresponding title. But how do we know the title?

The URL title is resolved by a :term:`crumb resolver`. By default two resolvers
are available: `_resolve_flatpage` and `_resolve_by_callback`.

The first one looks for a `FlatPage` object with given URL path in the database
(if `django.contrib.flatpages` is activated in settings). If this resolver
failed (i.e. flatpages are not available or there's no `FlatPage` with such URL
path), then next crumb resolver is called.

The crumb resolver `_resolve_by_callback` peeks into the URL maps and attempts
to resolve the URL into a view function. If such function is found, the
resolver looks whether the function has the "breadcrumb" attribute. This
attribute can be set by wrapping the view in decorator
:func:`navigation.decorators.breadcrumb`::

    from navigation.decorators import breadcrumb

    @breadcrumb('Hello')
    def say_hello(request):
        ...

    @breadcrumb(lambda request: u'%s settings' % request.user)
    def user_settings(request):
        ...

If the attribute is not found, we can't guess the name and give up. A dummy
breadcrumb is add to the trail.

However, we could also try "humanizing" the function's ``__name__`` attribute
or use a custom path-to-name mapping. You can do that easily by creating your
own crumb resolvers and registering them this way::

    from navigation.resolvers import crumb_resolver

    @crumb_resolver
    def my_custom_resolver_function(request, url):
        return Crumb(url, 'Hello!')

.. topic:: TODO

    I'll probably make this more explicit, e.g. add a settings variable like
    this::

        NAVIGATION_RESOLVERS = [
            'navigation.resolvers.resolve_flatpage',
            'navigation.resolvers.resolve_by_callback',
            'utils.navigation.my_custom_resolver_function',
        ]
