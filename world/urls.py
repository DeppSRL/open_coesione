from django.conf.urls import patterns, url
from world.views import TilesView

urlpatterns = patterns('',
    # faceted navigation
    # url(r'^tiles$', TilesView.as_view()),
    url(r'^tiles/(?P<layer_name>[^/]+)/(?P<z>[^/]+)/(?P<x>[^/]+)/(?P<y>[^/]+)\.(?P<extension>.+)$',
        TilesView.as_view(), name='tiles_url'),
)

