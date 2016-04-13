# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from soggetti.search_querysets import sqs
from soggetti.views import SoggettoView, SoggettoSearchView


urlpatterns = patterns('',
    # faceted navigation
    url(r'^$', SoggettoSearchView(template='soggetti/soggetto_search.html', searchqueryset=sqs, results_per_page=25), name='soggetti_search'),

    # dettaglio soggetto
    url(r'^(?P<slug>[\w-]+)/$', SoggettoView.as_view(), name='soggetti_soggetto'),
)
