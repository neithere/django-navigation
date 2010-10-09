Glossary
========

.. glossary::

    breadcrumbs
        a trail of links to higher-level documents. Represents levels of given
        URL path. For example, URL ``/news/2010/oct/`` corresponds to a
        document with heading "October 2010" and this path of breadcrumbs:
        
        * ``/news/`` "News"
        * ``/news/2010/`` "2010 news"

    crumb resolver
        a function that takes arguments `request` and `url` and returns either
        a :class:`navigation.helpers.Crumb` instance or `None`. Can be
        registered by using the decorator
        :func:`navigation.resolvers.crumb_resolver`::

            @crumb_resolver
            def custom_resolver(request, url):
                if url == '/secret/url/':
                    return Crumb(url, 'Hello')
                else:
                    return None  # pass to another resolver, if any
        
        If current URL is ``/secret/url/``, then the resolver will be called
        for both ``/secret/`` and ``/secret/url``. The resolver may not be
        called if another resolver did not return `None` for given URL (i.e.
        first resolver wins).

        If all resolvers returned `None` for a URL, then a dummy crumb is
        created. It can be told from a regular crumb in templates this way::

            {% if crumb.is_dummy %}
                <a href="{{ crumb.url }}">(???)</a>
            {% else %}
                <a href="{{ crumb.url }}">{{ crumb }}</a>
            {% endif %}

        This will produce the path of breadcrumbs like "(???) -> Hello" if
        ``/secret/url/`` could be resolved but ``/secret/`` couldn't.

    sections
        First-level URLs explicitly listed as `NAVIGATION_SECTIONS` setting
        (optional; only required by :func:`get_sections`).
