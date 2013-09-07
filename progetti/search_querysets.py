from haystack.query import SearchQuerySet
from progetti.views import ProgettoSearchView
from api.querysets import PatchedSearchResult
__author__ = 'guglielmo'

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
        highlight().order_by('-costo').result_class(PatchedSearchResult)

