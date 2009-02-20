# -*- coding: utf-8 -*-

# This file is _not_ intended to be imported by Python interpreter.

""" For a view to support Django Navigation, it should have the attribute named "navigation".
This attribute must be either a string or a callable that returns a string.
The resulting string will be used as title for the document at related path.
"""

###
# 1. A simple view with static label. Note the label being attached.
#

simple_view = lambda request: HttpResponse("This is some content")
simple_view.navigation = "This is a label"

###
# 2. A view handling date hierarchy ("/blog/2009/02/")
#

# filter objects by date parts (if any) and render template
@response('category_detail.html')
def entry_list(request,year=None, month=None):
    entry_list = Entry.objects.all()
    entry_list = filter_date(entry_list, 'pub_date', year, month)
    return dict(entry_list=entry_list)
# and now define the function to generate correct labels for each path level
def __nav(request, category_slug, year=None, month=None):
    category = get_object_or_404(Category, slug=category_slug)
    # path="/blog/2009/02/" -- show month name
    if year and month:
        return ru_strftime(u'%B', datetime.date(int(year),int(month),1))
    # path="/blog/2009/" -- show year
    if year:
        return year
    # path="/blog/" -- show static label for unfiltered list of objects
    return "Blog"
category_detail.navigation = __nav

###
# 3. A view that displays a single object within date hierarchy
#

# fetch object and render template
@response('entry_detail.html')
def entry_detail(request, category_slug, year, month, slug):
    entry = get_object_or_404(Entry, pub_date__year=year, pub_date__month=month, slug=slug)
    return dict(object=entry)
# and now define the function to find the label
#   (note that there can be further parts in the path; this view is not necessarily terminal
#   and chances are that only label may be needed for this object, so it's OK that it's looked up here)
def __nav(request, category_slug, year, month, slug):
    entry = get_object_or_404(Entry, category__slug=category_slug, pub_date__year=year, pub_date__month=month, slug=slug)
    return entry.title
entry_detail.navigation = __nav
