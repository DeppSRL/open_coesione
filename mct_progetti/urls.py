from django.conf.urls import patterns, url
from haystack.query import SearchQuerySet

from mct_progetti.views import (ProgettoSearchView)

## SearchQuerySet with multiple facets and highlight
sqs = SearchQuerySet().filter(django_ct='mct_progetti.progetto').\
      facet('tipo_operazione').\
      facet('priorita').\
      highlight()

urlpatterns = patterns('',
   # faceted navigation

   url(r'^$', ProgettoSearchView(template='progetti/progetto_search.html', searchqueryset=sqs), name='oc_progetto_search'),
)

