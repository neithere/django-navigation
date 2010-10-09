# -*- coding: utf-8 -*-
"""
Helpers
=======
"""
class Crumb(object):
    """ A navigation node.

    .. attribute:: url

        this breadcrumb's URL.

    .. attribute:: title

        this breadcrumb's title, as determined by the first successful
        :term:`crumb resolver`.

    .. attribute:: is_current

        `True` if this breadcrumb's URL corresponds to the current request
        path.

    .. attribute:: is_active

        `True` if current request path begins with this breadcrumb's URL.

    .. attribute:: is_dummy

        `True` if this breadcrumb is a stub, i.e. its URL could not be resolved
        by a :term:`crumb resolver`.

    """
    def __init__(self, url, title, is_current=False, is_active=False,
                 is_dummy=False):
        self.url        = url
        self.title      = title
        self.is_current = is_current
        self.is_active  = is_active
        self.is_dummy   = is_dummy

    def __unicode__(self):
        return unicode(self.title)

