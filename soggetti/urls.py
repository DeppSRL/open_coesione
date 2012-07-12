from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page
from haystack.query import SearchQuerySet
from soggetti.views import SoggettiView, SoggettoView, SoggettoSearchView


## SearchQuerySet with multiple facets and highlight
sqs = SearchQuerySet().filter(django_ct='soggetti.soggetto').\
    facet('ruolo').\
    facet('tema').\
    query_facet('costo', SoggettoSearchView.COST_RANGES['0-0TO100K']['qrange']).\
    query_facet('costo', SoggettoSearchView.COST_RANGES['1-100KTO1M']['qrange']).\
    query_facet('costo', SoggettoSearchView.COST_RANGES['2-1MTO10M']['qrange']).\
    query_facet('costo', SoggettoSearchView.COST_RANGES['3-10MTO100M']['qrange']).\
    query_facet('costo', SoggettoSearchView.COST_RANGES['4-100MTO1G']['qrange']).\
    query_facet('costo', SoggettoSearchView.COST_RANGES['5-1GTOINF']['qrange']).\
    query_facet('n_progetti', SoggettoSearchView.N_PROGETTI_RANGES['0-0TO10']['qrange']).\
    query_facet('n_progetti', SoggettoSearchView.N_PROGETTI_RANGES['1-10TO100']['qrange']).\
    query_facet('n_progetti', SoggettoSearchView.N_PROGETTI_RANGES['2-100TO1K']['qrange']).\
    query_facet('n_progetti', SoggettoSearchView.N_PROGETTI_RANGES['3-1KTO10K']['qrange']).\
    query_facet('n_progetti', SoggettoSearchView.N_PROGETTI_RANGES['4-10KTOINF']['qrange']).\
    highlight()

urlpatterns = patterns('',
   # faceted navigation
   url(r'^$', SoggettoSearchView(template='soggetti/soggetto_search.html', searchqueryset=sqs), name='soggetti_search'),

   # aggregato soggetti
   #url(r'^$', SoggettiView.as_view(), name='soggetti_soggetti'),

   # dettaglio soggetto
   url(r'^(?P<slug>[\w-]+)$', cache_page(key_prefix='soggetto')(SoggettoView.as_view()), name='soggetti_soggetto'),
)

