from django.conf.urls import url, patterns
from django.views.decorators.cache import cache_page

from territori.views import MapnikRegioniView, MapnikProvinceView, MapnikComuniView

urlpatterns = patterns('',
    url(r'^regioni.xml$',
        cache_page(key_prefix='mapnik_regioni')(MapnikRegioniView.as_view(filter=None)),
        name='territori_mapnick_regioni'),
    url(r'^province.xml$',
        cache_page(key_prefix='mapnik_province')(MapnikProvinceView.as_view(filter=None)),
        name='territori_mapnick_province'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/province.xml$',
        cache_page(key_prefix='mapnik_province_regione')(MapnikProvinceView.as_view(filter=None)),
        name='territori_mapnick_province_regione'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/comuni.xml$',
        cache_page(key_prefix='mapnik_comuni_regione')(MapnikComuniView.as_view(filter=None)),
        name='territori_mapnick_comuni_regione'),
    url(r'^province/(?P<cod_prov>[\d]+)/comuni.xml$',
        cache_page(key_prefix='mapnik_comuni_provincia')(MapnikComuniView.as_view(filter=None)),
        name='territori_mapnick_comuni_provincia'),
    url(r'^temi/(?P<slug>[-\w]+)/regioni.xml$',
        cache_page(key_prefix='mapnik_regioni_tema')(MapnikRegioniView.as_view(filter='tema')),
        name='territori_mapnick_regioni_tema'),
    url(r'^temi/(?P<slug>[-\w]+)/province.xml$',
        cache_page(key_prefix='mapnik_province_tema')(MapnikProvinceView.as_view(filter='tema')),
        name='territori_mapnick_province_tema'),
    url(r'^nature/(?P<slug>[-\w]+)/regioni.xml$',
        cache_page(key_prefix='mapnik_regioni_natura')(MapnikRegioniView.as_view(filter='natura')),
        name='territori_mapnick_regioni_natura'),
    url(r'^nature/(?P<slug>[-\w]+)/province.xml$',
        cache_page(key_prefix='mapnik_province_natura')(MapnikProvinceView.as_view(filter='natura')),
        name='territori_mapnick_province_natura'),
)