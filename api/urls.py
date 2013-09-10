from rest_framework.urlpatterns import format_suffix_patterns
from api.views import *
from django.conf.urls import patterns, url, include

__author__ = 'guglielmo'

urlpatterns = patterns('api.views',
    url(r'^$', 'api_root'),
    url(r'^progetti$', ProgettoList.as_view(), name='api-progetto-list'),
    url(r'^progetti/(?P<slug>[\w-]+)$', ProgettoDetail.as_view(), name='api-progetto-detail'),

    url(r'^soggetti$', SoggettoList.as_view(), name='api-soggetto-list'),
    url(r'^soggetti/(?P<slug>[\w-]+)$', SoggettoDetail.as_view(), name='api-soggetto-detail'),

    url(r'^temi$', TemaList.as_view(), name='api-tema-list'),
    url(r'^nature$', NaturaList.as_view(), name='api-natura-list'),
    url(r'^territori$', TerritorioList.as_view(), name='api-territorio-list'),
    url(r'^programmi$', ProgrammiList.as_view(), name='api-programma-list'),

    url(r'custom$', MyCustomView.as_view(), name='a-custom-view'),
)

# Login and logout views for the browsable API
urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])