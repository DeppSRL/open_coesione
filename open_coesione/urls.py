from django.conf.urls import patterns, include, url
from django.contrib.gis import admin
from django.conf import settings
from django.views.generic.base import TemplateView
from open_coesione.views import HomeView, FondiView, RisorseView, CGView, ContactView, PressView, SpesaCertificataView, \
    OpendataView, PilloleView, PillolaView, OpendataRedirectView, PilloleRedirectView, FAQView, EmbedPdfView
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

    # faq
    url(r'^faq/$', FAQView.as_view(lang='it'), name='faq-it'),
    url(r'^faq/en/$', FAQView.as_view(lang='en'), name='faq-en'),

    # api
    url(r'^api/', include('api.urls')),
    url(r'^widgets/', include('widgets.urls')),

    # list of urls to cache
    url(r'^full_cache_generator.txt$', CGView.as_view(), name='full_cache_generator'),
    url(r'^maps_cache_generator.txt$', CGView.as_view(filter='maps'), name='maps_cache_generator'),
    url(r'^pages_cache_generator.txt$', CGView.as_view(filter='pages'), name='pages_cache_generator'),

    # pre-csm page routes
    url(r'^progetto/$', TemplateView.as_view(template_name='flat/progetto.html'), name='oc-progetto-it'),
    url(r'^progetto/en/$', TemplateView.as_view(template_name='flat/project.html')),
    url(r'^project/$', TemplateView.as_view(template_name='flat/project.html'), name='oc-progetto-en'),
    url(r'^team/$', TemplateView.as_view(template_name='flat/team.html'), name='oc-team'),
    url(r'^gruppo-tecnico/$', TemplateView.as_view(template_name='flat/gruppo-tecnico.html'), name='oc-gruppo-tecnico'),
    url(r'^iniziative-internazionali/$', TemplateView.as_view(template_name='flat/iniziative-internazionali.html'), name='oc-eventi-internaizonali-it'),
    url(r'^international-events/$', TemplateView.as_view(template_name='flat/international-events.html'), name='oc-eventi-internazionali-en'),
    url(r'^termini-e-condizioni/$', TemplateView.as_view(template_name='flat/termini-e-condizioni.html'), name='oc-termini-e-condizioni'),
    url(r'^privacy/$', TemplateView.as_view(template_name='flat/privacy.html'), name='oc-privacy'),
    url(r'^contatti/$', ContactView.as_view(template_name='flat/contatti.html'), name='oc-contatti'),
    url(r'^licenza/$', TemplateView.as_view(template_name='flat/licenza.html'), name='oc-licenza'),
    url(r'^scopri-documenti-video/$', TemplateView.as_view(template_name='flat/scopri-documenti-video.html'), name='oc-scopri-documenti-video'),
    url(r'^scopri-newsletter-eventi/$', TemplateView.as_view(template_name='flat/scopri-newsletter-eventi.html'), name='oc-scopri-newsletter-eventi'),
    url(r'^sollecita-storie/$', TemplateView.as_view(template_name='flat/sollecita-storie.html'), name='oc-sollecita-storie'),
    url(r'^accessi/$', TemplateView.as_view(template_name='flat/accessi.html'), name='oc-accessi'),
    url(r'^riuso/$', TemplateView.as_view(template_name='flat/riuso.html'), name='oc-riuso'),

    url(r'^a-scuola-di-opencoesione/', TemplateView.as_view(template_name='flat/a_scuola_di_opencoesione.html')),
    url(r'^cerca-un-progetto/', TemplateView.as_view(template_name='flat/cerca_progetto.html')),
    url(r'^cerca-un-soggetto/', TemplateView.as_view(template_name='flat/cerca_soggetto.html')),
    url(r'^monitora-un-tema-o-un-territorio/', TemplateView.as_view(template_name='flat/monitoring.html')),
    url(r'^scheda-progetto/', TemplateView.as_view(template_name='flat/scheda_progetto.html')),
    url(r'^info-disponibili/', TemplateView.as_view(template_name='flat/info_disponibili.html')),

    url(r'^iscrizione-newsletter/', NLContactView.as_view(template_name='rubrica/newsletter_subscription.html'), name='rubrica-newsletter'),
    url(r'^fonti-di-finanziamento/', FondiView.as_view(template_name='flat/fonti_finanziamento.html')),
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

    url(r'^pdfview/(?P<embed_code>.+)$', EmbedPdfView.as_view(), name='pdfview'),

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

urlpatterns += patterns('django.contrib.flatpages.views',
    url(r'^about-us/$', 'flatpage', {'url': '/about-us/'}, name='about'),
)

