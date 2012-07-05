from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page
from haystack.query import SearchQuerySet

from progetti.views import ProgettoSearchView, ProgettoView, TipologiaView, TemaView

## SearchQuerySet with multiple facets and highlight
sqs = SearchQuerySet().filter(django_ct='progetti.progetto').\
        facet('natura').\
        facet('tema').\
        facet('regions').\
        query_facet('data_inizio', ProgettoSearchView.SIXMONTHS).\
        query_facet('data_inizio', ProgettoSearchView.ONEYEAR).\
        query_facet('data_inizio', ProgettoSearchView.TWOYEARS).\
        query_facet('costo', ProgettoSearchView.COST_RANGES['0TO1K']).\
        query_facet('costo', ProgettoSearchView.COST_RANGES['1KTO10K']).\
        query_facet('costo', ProgettoSearchView.COST_RANGES['10KTO100K']).\
        query_facet('costo', ProgettoSearchView.COST_RANGES['100KTOINF']).\
        highlight()

urlpatterns = patterns('',
   # faceted navigation
   url(r'^$', ProgettoSearchView(template='progetti/progetto_search.html', searchqueryset=sqs), name='progetti_search'),

   # dettaglio di progetto
   url(r'^(?P<slug>[\w-]+)$', ProgettoView.as_view(), name='progetti_progetto'),

   # tipologie
   url(r'^tipologie/(?P<slug>[\w-]+)$', cache_page()(TipologiaView.as_view()), name='progetti_tipologia'),

   # temi
   url(r'^temi/(?P<slug>[\w-]+)$', cache_page()(TemaView.as_view()), name='progetti_tema'),

)

