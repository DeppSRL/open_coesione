from django.conf.urls import patterns, url
from soggetti.views import SoggettiView, SoggettoView


urlpatterns = patterns('',
   # aggregato soggetti
   url(r'^$', SoggettiView.as_view(), name='soggetti_soggetti'),

   # dettaglio soggetto
   url(r'^(?P<slug>[\w-]+)$', SoggettoView.as_view(), name='soggetti_soggetto'),
)

