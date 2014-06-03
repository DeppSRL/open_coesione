from django.conf.urls import patterns, url
from blog.views import *

urlpatterns = patterns('',
    url(r'^$', BlogView.as_view(), name='blog_home'),
    # url(r'^tag/(?P<slug>[\w-]+)/$', BlogByTagView.as_view(), name='blog_by_tag'),
    # url(r'^date/(?P<date>[t|w|m|y])/$', BlogByDateView.as_view(), name='blog_by_date'),
)