from django.conf.urls import patterns, include, url
from django.contrib.gis import admin

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from open_coesione.views import HomeView


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'open_coesione.views.home', name='home'),
    # url(r'^open_coesione/', include('open_coesione.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # home
    url(r'^$', HomeView.as_view(), name='home'),

    # progetti
    url(r'^progetti/', include('progetti.urls')),

    # world
    url(r'^world/', include('world.urls')),

    # localita
    url(r'^localita/', include('localita.urls')),

)
