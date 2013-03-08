from django.conf import settings
from django.conf.urls import url, patterns
from django.views.decorators.cache import cache_page
from territori.views import LeafletView

urlpatterns = patterns('',
    url(r'^world.(?P<ext>(json|html))$', cache_page(settings.CACHE_PAGE_DURATION_SECS, LeafletView.as_view(layer='world'), key_prefix='leaflet_world'), name='territori_leaflet_world'),
    url(r'^regioni.(?P<ext>(json|html))$', cache_page(settings.CACHE_PAGE_DURATION_SECS, LeafletView.as_view(), key_prefix='leaflet_regioni'), name='territori_leaflet_regioni'),
    url(r'^province.(?P<ext>(json|html))$', cache_page(settings.CACHE_PAGE_DURATION_SECS, LeafletView.as_view(), key_prefix='leaflet_province'), name='territori_leaflet_province'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/province.(?P<ext>(json|html))$', cache_page(settings.CACHE_PAGE_DURATION_SECS, LeafletView.as_view(), key_prefix='leaflet_province_regione'), name='territori_leaflet_province_regione'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/comuni.(?P<ext>(json|html))$', cache_page(settings.CACHE_PAGE_DURATION_SECS, LeafletView.as_view(), key_prefix='leaflet_comuni_regione'), name='territori_leaflet_comuni_regione'),
    url(r'^province/(?P<cod_prov>[\d]+)/comuni.(?P<ext>(json|html))$', cache_page(settings.CACHE_PAGE_DURATION_SECS, LeafletView.as_view(), key_prefix='leaflet_comuni_provincia'), name='territori_leaflet_comuni_provincia'),
    url(r'^temi/(?P<slug>[-\w]+)/regioni.(?P<ext>(json|html))$', cache_page(settings.CACHE_PAGE_DURATION_SECS, LeafletView.as_view(filter='temi'), key_prefix='leaflet_regioni_tema'), name='territori_leaflet_regioni_tema'),
    url(r'^temi/(?P<slug>[-\w]+)/province.(?P<ext>(json|html))$', cache_page(settings.CACHE_PAGE_DURATION_SECS, LeafletView.as_view(filter='temi'), key_prefix='leaflet_province_tema'), name='territori_leaflet_province_tema'),
    url(r'^nature/(?P<slug>[-\w]+)/regioni.(?P<ext>(json|html))$', cache_page(settings.CACHE_PAGE_DURATION_SECS, LeafletView.as_view(filter='nature'), key_prefix='leaflet_regioni_natura'), name='territori_leaflet_regioni_natura'),
    url(r'^nature/(?P<slug>[-\w]+)/province.(?P<ext>(json|html))$', cache_page(settings.CACHE_PAGE_DURATION_SECS, LeafletView.as_view(filter='nature'), key_prefix='leaflet_province_natura'), name='territori_leaflet_province_natura'),
)