from django.conf.urls import patterns, include, url
from django.contrib.gis import admin
from django.conf import settings
from django.views.generic.base import TemplateView
from open_coesione.views import HomeView, FondiView, RisorseView

admin.autodiscover()

urlpatterns = patterns('',
    # admin documentation and reference
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # admin
    url(r'^admin/', include(admin.site.urls)),

    # home
    url(r'^$', HomeView.as_view(), name='home'),

    # progetti
    url(r'^progetti/', include('progetti.urls')),

    # soggetti
    url(r'^soggetti/', include('soggetti.urls')),

    # territori
    url(r'^territori/', include('territori.urls')),


    # pre-csm page routes
    url(r'^progetto/', TemplateView.as_view(template_name='flat/progetto.html')),
    url(r'^privacy/', TemplateView.as_view(template_name='flat/privacy.html')),
    url(r'^contatti/', TemplateView.as_view(template_name='flat/contatti.html')),
    url(r'^licenza/', TemplateView.as_view(template_name='flat/licenza.html')),

    url(r'^cerca-un-progetto/', TemplateView.as_view(template_name='flat/cerca_progetto.html')),
    url(r'^cerca-un-soggetto/', TemplateView.as_view(template_name='flat/cerca_soggetto.html')),
    url(r'^monitora-un-tema-o-un-territorio/', TemplateView.as_view(template_name='flat/monitoring.html')),
    url(r'^scheda-progetto/', TemplateView.as_view(template_name='flat/scheda_progetto.html')),
    url(r'^info-disponibili/', TemplateView.as_view(template_name='flat/info_disponibili.html')),
    url(r'^open-data/', TemplateView.as_view(template_name='flat/open_data.html')),

    url(r'^fonti-di-finanziamento/', FondiView.as_view(template_name='flat/fonti_finanziamento.html')),
    url(r'^pac/', RisorseView.as_view(template_name='flat/pac.html')),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    )

# feincms
urlpatterns += patterns('',
    url(r'', include('feincms.contrib.preview.urls')),
    url(r'', include('feincms.urls')),
)
