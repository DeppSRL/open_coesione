from django.conf.urls import patterns, include, url
from django.contrib.gis import admin
from django.conf import settings
from open_coesione.views import HomeView

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
    # url(r'^soggetti/', include('soggetti.urls')),

    # territori
    url(r'^territori/', include('territori.urls')),



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
