# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from blog.views import *


urlpatterns = patterns('',
    url(r'^$', BlogView.as_view(), name='blog_home'),
    url(r'^articolo/(?P<slug>[\w-]+)/$', BlogEntryView.as_view(), name='blog_item'),
    url(r'^load/(?P<slug>[\w-]+)/$', blog_entry_item, name='blog_item_load'),
)
