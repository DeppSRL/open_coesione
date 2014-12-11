from rest_framework.urlpatterns import format_suffix_patterns
from api.views import *
from django.conf.urls import patterns, url, include

__author__ = 'guglielmo'

urlpatterns = patterns('api.views',
    url(r'^$', 'api_root', name='api-root'),
    url(r'^progetti$', ProgettoList.as_view(), name='api-progetto-list'),
    url(r'^progetti/(?P<slug>[\w-]+)$', ProgettoDetail.as_view(), name='api-progetto-detail'),

    url(r'^soggetti$', SoggettoList.as_view(), name='api-soggetto-list'),
    url(r'^soggetti/(?P<slug>[\w-]+)$', SoggettoDetail.as_view(), name='api-soggetto-detail'),

    url(r'^aggregati$', AggregatoView.as_view(), name='api-aggregati-home'),
    url(r'^aggregati/temi$', 'api_aggregati_temi_list', name='api-aggregati-tema-list'),
    url(r'^aggregati/temi/(?P<slug>[\w-]+)$', AggregatoTemaDetailView.as_view(), name='api-aggregati-tema-detail'),
    url(r'^aggregati/nature$', 'api_aggregati_nature_list', name='api-aggregati-natura-list'),
    url(r'^aggregati/nature/(?P<slug>[\w-]+)$', AggregatoNaturaDetailView.as_view(), name='api-aggregati-natura-detail'),
    url(r'^aggregati/territori$', 'api_aggregati_territori_list', name='api-aggregati-territorio-list'),
    url(r'^aggregati/territori/(?P<slug>[\w-]+)$', AggregatoTerritorioDetailView.as_view(), name='api-aggregati-territorio-detail'),
    # url(r'^aggregati/programmi$', AggregatoProgrammaListView.as_view(), name='api-aggregati-programma-list'),
    # url(r'^aggregati/programmi/(?P<code>[\d]+)$', AggregatoProgrammaDetailView.as_view(), name='api-aggregati-programma-detail'),

    url(r'^temi$', TemaList.as_view(), name='api-tema-list'),
    url(r'^nature$', NaturaList.as_view(), name='api-natura-list'),
    url(r'^territori$', TerritorioList.as_view(), name='api-territorio-list'),
    url(r'^programmi$', ProgrammiList.as_view(), name='api-programma-list'),
    url(r'^classificazioni$', ClassificazioneList.as_view(), name='api-classificazione-list'),
    url(r'^classificazioni-cup$', ClassificazioneCupList.as_view(), name='api-classificazione-cup-list'),

)

# Login and logout views for the browsable API
urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])