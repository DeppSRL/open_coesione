from django.conf.urls import patterns, url
from haystack.query import SearchQuerySet

from progetti.views import ProgettoSearchView, ProgettoView, TipologiaView, TemaView

## SearchQuerySet with multiple facets and highlight
sqs = SearchQuerySet().filter(django_ct='progetti.progetto').\
      facet('tipo_operazione').\
      facet('priorita').\
      highlight()

urlpatterns = patterns('',
   # faceted navigation
   url(r'^$', ProgettoSearchView(template='progetti/progetto_search.html', searchqueryset=sqs), name='progetti_search'),

   # dettaglio di progetto
   url(r'^(?P<slug>[\w-]+)$', ProgettoView.as_view(), name='progetti_progetto'),

   # tipologie
   url(r'^tipologie/(?P<slug>[\w-]+)$', TipologiaView.as_view(), name='progetti_tipologia'),

   # temi
   url(r'^temi/(?P<slug>[\w-]+)$', TemaView.as_view(), name='progetti_tema'),

)

