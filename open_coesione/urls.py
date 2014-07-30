from django.conf.urls import patterns, include, url
from django.contrib.gis import admin
from django.conf import settings
from django.views.generic.base import TemplateView, RedirectView
from open_coesione.views import HomeView, FondiView, RisorseView, ContactView, PressView, SpesaCertificataView, \
    OpendataView, PilloleView, PillolaView, OpendataRedirectView, PilloleRedirectView, FAQView, DatiISTATView, \
    DocumentsRedirectView
from rubrica.views import NLContactView
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
    url(r'^$', HomeView.as_view(), name='home'),

    # progetti
    url(r'^progetti/', include('progetti.urls')),

    # soggetti
    url(r'^soggetti/', include('soggetti.urls')),

    # territori
    url(r'^territori/', include('territori.urls')),

    # blog
    url(r'^news/', include('blog.urls')),

    # pillole
    url(r'^pillole/(?P<path>.+)$', PilloleRedirectView.as_view(), name='pillole_clean'),
    url(r'^pillole/$', PilloleView.as_view(), name='pillole'),
    url(r'^pillola/(?P<slug>[\w-]+)/$', PillolaView.as_view(), name='pillola_item'),

    # dati ISTAT di contesto
    url(r'^dati-istat-di-contesto/$', DatiISTATView.as_view(), name='dati-istat'),

    # faq
    url(r'^faq/$', FAQView.as_view(lang='it'), name='faq-it'),
    url(r'^faq/en/$', FAQView.as_view(lang='en'), name='faq-en'),

    # api
    url(r'^api/', include('api.urls')),
    url(r'^widgets/', include('widgets.urls')),

    # pre-csm page routes
    # TODO: move into flatpages
#    url(r'^progetto/$', TemplateView.as_view(template_name='flat/progetto.html'), name='oc-progetto-it'),
    url(r'^progetto/en/$', TemplateView.as_view(template_name='flat/project.html')),
    url(r'^project/$', TemplateView.as_view(template_name='flat/project.html'), name='oc-progetto-en'),
    url(r'^a-scuola-di-opencoesione/', TemplateView.as_view(template_name='flat/a_scuola_di_opencoesione.html')),
    url(r'^cerca-un-progetto/', TemplateView.as_view(template_name='flat/cerca_progetto.html')),
    url(r'^privacy/$', TemplateView.as_view(template_name='flat/privacy.html'), name='oc-privacy'),
    url(r'^contatti/$', ContactView.as_view(template_name='flat/contatti.html'), name='oc-contatti'),
    url(r'^licenza/$', TemplateView.as_view(template_name='flat/licenza.html'), name='oc-licenza'),
    url(r'^cerca-un-soggetto/', TemplateView.as_view(template_name='flat/cerca_soggetto.html')),
    url(r'^scheda-progetto/', TemplateView.as_view(template_name='flat/scheda_progetto.html')),
    url(r'^info-disponibili/', TemplateView.as_view(template_name='flat/info_disponibili.html')),

    url(r'^seguici/', NLContactView.as_view(template_name='rubrica/newsletter_subscription.html'), name='rubrica-newsletter'),
    url(r'^iscrizione-newsletter/', RedirectView.as_view(url='/seguici/')),
    url(r'^fonti-di-finanziamento/', FondiView.as_view(template_name='flat/fonti_finanziamento.html'), name='fonti-finanziamento'),
    url(r'^pac/', RisorseView.as_view(template_name='flat/pac.html')),
    url(r'^api-faq/', RisorseView.as_view(template_name='flat/api.html'), name='api-faq'),
    url(r'^spesa-certificata/',
        SpesaCertificataView.as_view(template_name='flat/spesa_certificata.html'),
                                     name='flat-spesa-certificata'),
    url(r'^spesa-certificata-grafici/',
        SpesaCertificataView.as_view(template_name='flat/spesa_certificata_grafici.html'),
                                     name='flat-spesa-certificata-grafici'),

    url(r'^rassegna-stampa/', PressView.as_view()),

    url(r'^opendata/(?P<path>.+)$', OpendataRedirectView.as_view(), name='opendata_clean'),
    url(r'^opendata/$', OpendataView.as_view(template_name='flat/open_data.html'), name='opendata'),

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


