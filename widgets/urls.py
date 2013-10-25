from django.conf.urls import patterns, url
from widgets.views import WidgetBuilderView, WidgetView


__author__ = 'daniele'


urlpatterns = patterns('',
    url(r'^$', WidgetBuilderView.as_view(), name='widgets-select'),
    url(r'^(?P<widget>[_\w]+)/$', WidgetView.as_view(), name='widgets-detail'),
    url(r'^(?P<widget>[_\w]+)/build/$', WidgetBuilderView.as_view(), name='widgets-build'),
)
