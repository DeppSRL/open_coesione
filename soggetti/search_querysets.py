# -*- coding: utf-8 -*-
from haystack.query import SearchQuerySet
from api.querysets import PatchedSearchResult
from soggetti.views import SoggettoSearchView


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
    highlight().order_by('-costo').result_class(PatchedSearchResult)
