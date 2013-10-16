from django.conf.urls import patterns, url
from widgets.views import WidgetView, WidgetBuilderView


__author__ = 'daniele'


urlpatterns = patterns('',
    url(r'^$', WidgetBuilderView.as_view(), name='widgets-builder'),
    url(r'^(?P<widget>[\w-]+)/$', WidgetView.as_view(), name='widget'),
)
