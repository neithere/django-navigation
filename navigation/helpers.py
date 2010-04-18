# -*- coding: utf-8 -*-

class Crumb(object):
    "A navigation node."
    def __init__(self, url, title, is_current=False, is_dummy=False):
        self.url        = url
        self.title      = title
        self.is_current = is_current
        self.is_dummy   = is_dummy

    def __unicode__(self):
        return unicode(self.title)

