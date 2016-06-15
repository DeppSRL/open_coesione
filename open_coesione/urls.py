# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.gis import admin
from django.views.generic.base import TemplateView
from views import HomeView, FondiView, RisorsaView, ContactView, SpesaCertificataGraficiView,\
    OpendataView, OpendataRedirectView, PillolaListView, PillolaDetailView, DocumentsRedirectView, FAQListView,\
    PressReviewListView, DatiISTATView, SpesaCertificataView, IndicatoriAccessoView
from filebrowser.sites import site


admin.autodiscover()


urlpatterns = patterns('',
    # admin documentation and reference
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # admin
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # home
    url(r'^$', HomeView.as_view(template_name='homepage.html'), name='home'),

    # progetti
    url(r'^progetti/', include('progetti.urls')),

    # soggetti
    url(r'^soggetti/', include('soggetti.urls')),

    # territori
    url(r'^territori/', include('territori.urls')),

    # blog
    url(r'^news/', include('blog.urls')),

    # charts
    url(r'^charts/', include('open_coesione.charts.urls')),

    # url shortener
    url(r'^su/', include('urlshortener.urls')),

    # pillole
    url(r'^pillole/$', PillolaListView.as_view(), name='pillole'),
    url(r'^pillola/(?P<slug>[\w-]+)/$', PillolaDetailView.as_view(), name='pillola'),

    # faq
    url(r'^faq/$', FAQListView.as_view(lang='it'), name='faq-it'),
    url(r'^faq/en/$', FAQListView.as_view(lang='en'), name='faq-en'),

    # api
    url(r'^api/', include('api.urls')),
    url(r'^widgets/', include('widgets.urls')),

    # pre-csm page routes
    # TODO: move into flatpages
    url(r'^progetto/en/$', TemplateView.as_view(template_name='flat/project.html')),
    url(r'^project/$', TemplateView.as_view(template_name='flat/project.html'), name='oc-progetto-en'),
    url(r'^a-scuola-di-opencoesione/', TemplateView.as_view(template_name='flat/a_scuola_di_opencoesione.html')),
    url(r'^cerca-un-progetto/', TemplateView.as_view(template_name='flat/cerca_progetto.html')),
    url(r'^contatti/$', ContactView.as_view(template_name='flat/contatti.html'), name='oc-contatti'),
    url(r'^cerca-un-soggetto/', TemplateView.as_view(template_name='flat/cerca_soggetto.html')),
    url(r'^scheda-progetto/', TemplateView.as_view(template_name='flat/scheda_progetto.html')),
    url(r'^info-disponibili/', TemplateView.as_view(template_name='flat/info_disponibili.html')),
    url(r'^api-faq/', TemplateView.as_view(template_name='flat/api.html'), name='api-faq'),

    url(r'^dati-istat-di-contesto/$', DatiISTATView.as_view(template_name='open_coesione/dati_istat.html'), name='dati-istat'),

    url(r'^indicatori_di_accesso/$', IndicatoriAccessoView.as_view(lang='it', template_name='open_coesione/indicatori_accesso.html'), name='indicatori-accesso-it'),
    url(r'^access_indicators/$', IndicatoriAccessoView.as_view(lang='en', template_name='open_coesione/indicatori_accesso.html'), name='indicatori-accesso-en'),

    url(r'^segui/', TemplateView.as_view(template_name='open_coesione/newsletter.html'), name='newsletter'),

    url(r'^rassegna-stampa/', PressReviewListView.as_view()),

    url(r'^pac/', RisorsaView.as_view(template_name='open_coesione/pac.html'), name='pac'),
    url(r'^spesa-certificata/', SpesaCertificataView.as_view(template_name='open_coesione/spesa_certificata.html'), name='spesa-certificata'),
    url(r'^spesa-certificata-grafici/', SpesaCertificataGraficiView.as_view(template_name='open_coesione/spesa_certificata_grafici.html'), name='spesa-certificata-grafici'),
    url(r'^fonti-di-finanziamento/$', FondiView.as_view(template_name='open_coesione/fonti_finanziamento.html'), name='fonti-finanziamento'),
    url(r'^risorse_2014_2020/$', FondiView.as_view(template_name='open_coesione/fonti_finanziamento_1420.html'), name='fonti-finanziamento-1420'),


    url(r'^opendata/(?P<path>.+)$', OpendataRedirectView.as_view(), name='opendata_clean'),
    url(r'^opendata/$', OpendataView.as_view(template_name='open_coesione/opendata.html'), name='opendata'),

    url(r'^documenti/(?P<path>.+)$', DocumentsRedirectView.as_view(), name='documents_clean'),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    )

#tinymce
urlpatterns += patterns('',
    (r'^tinymce/', include('tinymce.urls')),
)
