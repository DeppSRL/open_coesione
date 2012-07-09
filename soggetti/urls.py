from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page
from soggetti.views import SoggettiView, SoggettoView


urlpatterns = patterns('',
   # aggregato soggetti
   url(r'^$', SoggettiView.as_view(), name='soggetti_soggetti'),

   # dettaglio soggetto
   url(r'^(?P<slug>[\w-]+)$', cache_page(key_prefix='soggetto')(SoggettoView.as_view()), name='soggetti_soggetto'),
)

