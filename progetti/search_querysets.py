# -*- coding: utf-8 -*-
from haystack.query import SearchQuerySet
from oc_search.forms import format_facet_field
from views import ProgettoSearchView


sqs = SearchQuerySet().filter(django_ct='progetti.progetto').order_by('-costo')

for name in ('is_scuola', 'is_active', 'natura', 'tema', 'fonte', 'stato_progetto'):
    sqs = sqs.facet(format_facet_field(name))

for name in ProgettoSearchView.RANGES:
    for range in ProgettoSearchView.RANGES[name]:
        sqs = sqs.query_facet(format_facet_field(name), ProgettoSearchView.RANGES[name][range]['qrange'])
