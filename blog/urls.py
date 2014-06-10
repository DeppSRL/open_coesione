from django.conf.urls import patterns, url
from blog.views import *

urlpatterns = patterns('',
    url(r'^$', BlogView.as_view(), name='blog_home'),
    url(r'^articolo/(?P<slug>[\w-]+)/$', BlogEntryView.as_view(), name='blog_item'),
    url(r'^load/(?P<slug>[\w-]+)/$', blogEntryItem, name='blog_item_load'),
    # url(r'^tag/(?P<slug>[\w-]+)/$', BlogByTagView.as_view(), name='blog_by_tag'),
    # url(r'^date/(?P<date>[t|w|m|y])/$', BlogByDateView.as_view(), name='blog_by_date'),
)