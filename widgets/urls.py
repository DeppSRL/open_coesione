from django.conf.urls import patterns, url
from widgets.views import WidgetBuilderView, TerritorioWidgetView, NaturaWidgetView, TemaWidgetView


__author__ = 'daniele'


urlpatterns = patterns('',
    url(r'^$', WidgetBuilderView.as_view(), name='widgets-builder'),
    url(r'^territorio/$', TerritorioWidgetView.as_view(), name='widget-territorio'),
    url(r'^natura/$', NaturaWidgetView.as_view(), name='widget-natura'),
    url(r'^tema/$', TemaWidgetView.as_view(), name='widget-tema'),
)
