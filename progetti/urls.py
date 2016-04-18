# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from progetti.search_querysets import sqs
from progetti.views import ProgettoSearchView, ProgettoView, ClassificazioneAzioneView, ClassificazioneAzioneCSVView,\
    TemaCSVView, TemaView, SegnalaDescrizioneView, SegnalazioneDetailView, ProgettoCSVSearchView,\
    ProgettoLocCSVSearchView, ProgrammaView, ProgrammiView, ProgettoPagamentiCSVView


urlpatterns = patterns('',
    # faceted navigation
    url(r'^$', ProgettoSearchView(template='progetti/progetto_search.html', searchqueryset=sqs, results_per_page=10), name='progetti_search'),
    url(r'^csv_prog/$', ProgettoCSVSearchView(searchqueryset=sqs), name='progetti_search_csv'),
    url(r'^csv_loc/$', ProgettoLocCSVSearchView(searchqueryset=sqs), name='progetti_search_csv_loc'),

    url(r'^segnalazione/$', SegnalaDescrizioneView.as_view(), name='progetti_segnalazione'),
    url(r'^segnalazione/completa/$', TemplateView.as_view(template_name='segnalazione/completata.html'), name='progetti_segnalazione_completa'),
    url(r'^segnalazione/(?P<pk>\d+)/$', SegnalazioneDetailView.as_view(), name='progetto_segnalazione_pubblicata'),

    # dettaglio progetto
    url(r'^(?P<slug>[\w-]+)/$', ProgettoView.as_view(), name='progetti_progetto'),
    url(r'^pagamenti_(?P<slug>[\w-]+).csv$', ProgettoPagamentiCSVView.as_view(), name='progetto_pagamenti'),

    # tipologie
    url(r'^tipologie/(?P<slug>[\w-]+)/$', ClassificazioneAzioneView.as_view(), name='progetti_tipologia'),
    # csv comuni procapite per natura
    url(r'^tipologie/(?P<slug>[\w-]+).csv$', cache_page(settings.CACHE_PAGE_DURATION_SECS, ClassificazioneAzioneCSVView.as_view(), key_prefix='tipologie'), name='progetti_tipologia_csv'),

    # temi
    url(r'^temi/(?P<slug>[\w-]+)/$', TemaView.as_view(), name='progetti_tema'),
    # csv comuni procapite per tema
    url(r'^temi/(?P<slug>[\w-]+).csv$', cache_page(settings.CACHE_PAGE_DURATION_SECS, TemaCSVView.as_view(), key_prefix='temi'), name='progetti_tema_csv'),

    # programmi
    url(r'^programmi/(?P<codice>[\w]+)/$', ProgrammaView.as_view(), name='progetti_programma'),

    # gruppo programmi
    url(r'^gruppo-programmi/(?P<slug>[\w-]+)/$', ProgrammiView.as_view(), name='progetti_programmi'),
)
