from django.conf import settings
from django.conf.urls import url, patterns
from django.views.decorators.cache import cache_page

from territori.views import MapnikRegioniView, MapnikProvinceView, MapnikComuniView

urlpatterns = patterns('',
    url(r'^regioni.xml$',
        cache_page(settings.CACHE_PAGE_DURATION_SECS, MapnikRegioniView.as_view(filter=None), key_prefix='mapnik_regioni'),
        name='territori_mapnick_regioni'),
    url(r'^province.xml$',
        cache_page(settings.CACHE_PAGE_DURATION_SECS, MapnikProvinceView.as_view(filter=None), key_prefix='mapnik_province'),
        name='territori_mapnick_province'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/province.xml$',
        cache_page(settings.CACHE_PAGE_DURATION_SECS, MapnikProvinceView.as_view(filter=None), key_prefix='mapnik_province_regione'),
        name='territori_mapnick_province_regione'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/comuni.xml$',
        cache_page(settings.CACHE_PAGE_DURATION_SECS, MapnikComuniView.as_view(filter=None), key_prefix='mapnik_comuni_regione'),
        name='territori_mapnick_comuni_regione'),
    url(r'^province/(?P<cod_prov>[\d]+)/comuni.xml$',
        cache_page(settings.CACHE_PAGE_DURATION_SECS, MapnikComuniView.as_view(filter=None), key_prefix='mapnik_comuni_provincia'),
        name='territori_mapnick_comuni_provincia'),
    url(r'^temi/(?P<slug>[-\w]+)/regioni.xml$',
        cache_page(settings.CACHE_PAGE_DURATION_SECS, MapnikRegioniView.as_view(filter='tema'), key_prefix='mapnik_regioni_tema'),
        name='territori_mapnick_regioni_tema'),
    url(r'^temi/(?P<slug>[-\w]+)/province.xml$',
        cache_page(settings.CACHE_PAGE_DURATION_SECS, MapnikProvinceView.as_view(filter='tema'), key_prefix='mapnik_province_tema'),
        name='territori_mapnick_province_tema'),
    url(r'^nature/(?P<slug>[-\w]+)/regioni.xml$',
        cache_page(settings.CACHE_PAGE_DURATION_SECS, MapnikRegioniView.as_view(filter='natura'), key_prefix='mapnik_regioni_natura'),
        name='territori_mapnick_regioni_natura'),
    url(r'^nature/(?P<slug>[-\w]+)/province.xml$',
        cache_page(settings.CACHE_PAGE_DURATION_SECS, MapnikProvinceView.as_view(filter='natura'), key_prefix='mapnik_province_natura'),
        name='territori_mapnick_province_natura'),
)