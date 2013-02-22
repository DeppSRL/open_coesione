from django.conf.urls import patterns, include, url
from django.contrib.gis import admin
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from open_coesione.views import HomeView, FondiView, RisorseView, CGView, ContactView, PressView, SpesaCertificataView

admin.autodiscover()

urlpatterns = patterns('',
    # admin documentation and reference
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # admin
    url(r'^admin/', include(admin.site.urls)),

    # home
    url(r'^$', cache_page()(HomeView.as_view()), name='home'),

    # progetti
    url(r'^progetti/', include('progetti.urls')),

    # soggetti
    url(r'^soggetti/', include('soggetti.urls')),

    # territori
    url(r'^territori/', include('territori.urls')),

    # blog
    url(r'^news/', include('blog.urls')),

    # list of urls to cache
    url(r'^full_cache_generator.txt$', CGView.as_view(), name='full_cache_generator'),
    url(r'^maps_cache_generator.txt$', CGView.as_view(filter='maps'), name='maps_cache_generator'),
    url(r'^pages_cache_generator.txt$', CGView.as_view(filter='pages'), name='pages_cache_generator'),

    # pre-csm page routes
    url(r'^progetto/$', TemplateView.as_view(template_name='flat/progetto.html')),
    url(r'^progetto/en/$', TemplateView.as_view(template_name='flat/progetto_en.html')),
    url(r'^privacy/', TemplateView.as_view(template_name='flat/privacy.html')),
    url(r'^contatti/', ContactView.as_view(template_name='flat/contatti.html'), name='oc_contatti'),
    url(r'^licenza/', TemplateView.as_view(template_name='flat/licenza.html')),

    url(r'^cerca-un-progetto/', TemplateView.as_view(template_name='flat/cerca_progetto.html')),
    url(r'^cerca-un-soggetto/', TemplateView.as_view(template_name='flat/cerca_soggetto.html')),
    url(r'^monitora-un-tema-o-un-territorio/', TemplateView.as_view(template_name='flat/monitoring.html')),
    url(r'^scheda-progetto/', TemplateView.as_view(template_name='flat/scheda_progetto.html')),
    url(r'^info-disponibili/', TemplateView.as_view(template_name='flat/info_disponibili.html')),
    url(r'^open-data/', TemplateView.as_view(template_name='flat/open_data.html')),
    url(r'^faq/$', TemplateView.as_view(template_name='flat/faq.html')),
    url(r'^faq/en/$', TemplateView.as_view(template_name='flat/faq_en.html')),

    url(r'^fonti-di-finanziamento/', FondiView.as_view(template_name='flat/fonti_finanziamento.html')),
    url(r'^pac/', RisorseView.as_view(template_name='flat/pac.html')),
    url(r'^spesa-certificata/', SpesaCertificataView.as_view(template_name='flat/spesa_certificata.html')),

    url(r'^rassegna-stampa/', PressView.as_view()),

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