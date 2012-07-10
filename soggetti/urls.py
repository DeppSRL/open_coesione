from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page
from haystack.query import SearchQuerySet
from soggetti.views import SoggettiView, SoggettoView, SoggettoSearchView


## SearchQuerySet with multiple facets and highlight
sqs = SearchQuerySet().filter(django_ct='soggetti.soggetto').\
    facet('ruolo').\
    facet('tema').\
    highlight()

urlpatterns = patterns('',
   # faceted navigation
   url(r'^$', SoggettoSearchView(template='soggetti/soggetto_search.html', searchqueryset=sqs), name='soggetti_search'),

   # aggregato soggetti
   url(r'^$', SoggettiView.as_view(), name='soggetti_soggetti'),

   # dettaglio soggetto
   url(r'^(?P<slug>[\w-]+)$', cache_page(key_prefix='soggetto')(SoggettoView.as_view()), name='soggetti_soggetto'),
)

