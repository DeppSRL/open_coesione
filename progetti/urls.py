from django.conf import settings
from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from haystack.query import SearchQuerySet

from progetti.views import ProgettoSearchView, ProgettoView, TipologiaView, TipologiaCSVView, TemaCSVView, TemaView, SegnalaDescrizioneView, SegnalazioneDetailView, ProgettoCSVSearchView, ProgettoCSVPreviewSearchView, ProgettoLocCSVPreviewSearchView, ProgettoLocCSVSearchView, ProgettoFullCSVSearchView

## SearchQuerySet with multiple facets and highlight
sqs = SearchQuerySet().filter(django_ct='progetti.progetto').\
        facet('natura').\
        facet('tema').\
        facet('fonte').\
        query_facet('data_inizio', ProgettoSearchView.DATE_INTERVALS_RANGES['2013']['qrange']).\
        query_facet('data_inizio', ProgettoSearchView.DATE_INTERVALS_RANGES['2012']['qrange']).\
        query_facet('data_inizio', ProgettoSearchView.DATE_INTERVALS_RANGES['2011']['qrange']).\
        query_facet('data_inizio', ProgettoSearchView.DATE_INTERVALS_RANGES['2010']['qrange']).\
        query_facet('data_inizio', ProgettoSearchView.DATE_INTERVALS_RANGES['2009']['qrange']).\
        query_facet('data_inizio', ProgettoSearchView.DATE_INTERVALS_RANGES['2008']['qrange']).\
        query_facet('data_inizio', ProgettoSearchView.DATE_INTERVALS_RANGES['2007']['qrange']).\
        query_facet('data_inizio', ProgettoSearchView.DATE_INTERVALS_RANGES['early']['qrange']).\
        query_facet('data_inizio', ProgettoSearchView.DATE_INTERVALS_RANGES['nd']['qrange']).\
        query_facet('costo', ProgettoSearchView.COST_RANGES['0-0TO1K']['qrange']).\
        query_facet('costo', ProgettoSearchView.COST_RANGES['1-1KTO10K']['qrange']).\
        query_facet('costo', ProgettoSearchView.COST_RANGES['2-10KTO100K']['qrange']).\
        query_facet('costo', ProgettoSearchView.COST_RANGES['3-100KTOINF']['qrange']).\
        query_facet('perc_pagamento', ProgettoSearchView.PERC_PAY_RANGES['0-0TO25']['qrange']).\
        query_facet('perc_pagamento', ProgettoSearchView.PERC_PAY_RANGES['1-25TO50']['qrange']).\
        query_facet('perc_pagamento', ProgettoSearchView.PERC_PAY_RANGES['2-50TO75']['qrange']).\
        query_facet('perc_pagamento', ProgettoSearchView.PERC_PAY_RANGES['3-75TO100']['qrange']).\
        highlight().order_by('-costo')


urlpatterns = patterns('',
   # faceted navigation
   url(r'^$', ProgettoSearchView(template='progetti/progetto_search.html', searchqueryset=sqs), name='progetti_search'),
   url(r'^csv_preview/$', ProgettoCSVPreviewSearchView(template='progetti/progetto_search_csv.html', searchqueryset=sqs), name='progetti_search_csv_preview'),
   url(r'^csv_loc_preview/$', ProgettoLocCSVPreviewSearchView(template='', searchqueryset=sqs), name='progetti_search_csv_loc_preview'),
   url(r'^csv_prog/$', ProgettoCSVSearchView(searchqueryset=sqs), name='progetti_search_csv'),
   url(r'^csv_loc/$', ProgettoLocCSVSearchView(searchqueryset=sqs), name='progetti_search_csv_loc'),
   url(r'^csv_full/$', ProgettoFullCSVSearchView(searchqueryset=sqs), name='progetti_search_csv_full_archive'),
#    url(r'^json/$', ProgettoJSONSearchView(template='progetti/progetto_search_csv.html', searchqueryset=sqs), name='progetti_search_csv'),

   url(r'^segnalazione/$', SegnalaDescrizioneView.as_view(), name='progetti_segnalazione'),
   url(r'^segnalazione/completa/$', TemplateView.as_view(template_name='segnalazione/completata.html'), name='progetti_segnalazione_completa'),
   url(r'^segnalazione/(?P<pk>\d+)/$', SegnalazioneDetailView.as_view(), name='progetto_segnalazione_pubblicata'),

   # dettaglio di progetto
   url(r'^(?P<slug>[\w-]+)/$', ProgettoView.as_view(), name='progetti_progetto'),

   # tipologie
   url(r'^tipologie/(?P<slug>[\w-]+)/$', TipologiaView.as_view(), name='progetti_tipologia'),
   # csv comuni procapite per natura
   url(r'^tipologie/(?P<slug>[\w-]+).csv$', cache_page(settings.CACHE_PAGE_DURATION_SECS, TipologiaCSVView.as_view(), key_prefix='tipologie'), name='progetti_tipologia_csv'),

   # temi
   url(r'^temi/(?P<slug>[\w-]+)/$', TemaView.as_view(), name='progetti_tema'),
    # csv comuni procapite per tema
    url(r'^temi/(?P<slug>[\w-]+).csv$', cache_page(settings.CACHE_PAGE_DURATION_SECS, TemaCSVView.as_view(), key_prefix='temi'), name='progetti_tema_csv'),


)

