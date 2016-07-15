from django.conf.urls import patterns, url
from views import indicatori, indicatori_regionali


urlpatterns = patterns('',
    url(r'^indicatori/$', indicatori),
    url(r'^indicatori-regionali/(?P<indicatore_id>\d{3})/$', indicatori_regionali),
)
