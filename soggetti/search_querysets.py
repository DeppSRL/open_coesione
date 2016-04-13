# -*- coding: utf-8 -*-
from haystack.query import SearchQuerySet
from oc_search.forms import format_facet_field
from views import SoggettoSearchView


sqs = SearchQuerySet().filter(django_ct='soggetti.soggetto').order_by('-costo')

for name in ('ruolo', 'tema'):
    sqs = sqs.facet(format_facet_field(name))

for name in SoggettoSearchView.RANGES:
    for range in SoggettoSearchView.RANGES[name]:
        sqs = sqs.query_facet(format_facet_field(name), SoggettoSearchView.RANGES[name][range]['qrange'])
