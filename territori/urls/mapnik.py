from django.conf import settings
from django.conf.urls import url, patterns
from django.views.decorators.cache import cache_page

from territori.views import MapnikRegioniView, MapnikProvinceView, MapnikComuniView

urlpatterns = patterns('',
    url(r'^regioni.xml$',
        MapnikRegioniView.as_view(filter=None), name='territori_mapnik_regioni'),
    url(r'^province.xml$',
        MapnikProvinceView.as_view(filter=None), name='territori_mapnik_province'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/province.xml$',
        MapnikProvinceView.as_view(filter=None), name='territori_mapnik_province_regione'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/comuni.xml$',
        MapnikComuniView.as_view(filter=None), name='territori_mapnik_comuni_regione'),
    url(r'^province/(?P<cod_prov>[\d]+)/comuni.xml$',
        MapnikComuniView.as_view(filter=None), name='territori_mapnik_comuni_provincia'),
    url(r'^temi/(?P<slug>[-\w]+)/regioni.xml$',
        MapnikRegioniView.as_view(filter='tema'), name='territori_mapnik_regioni_tema'),
    url(r'^temi/(?P<slug>[-\w]+)/province.xml$',
        MapnikProvinceView.as_view(filter='tema'), name='territori_mapnik_province_tema'),
    url(r'^nature/(?P<slug>[-\w]+)/regioni.xml$',
        MapnikRegioniView.as_view(filter='natura'), name='territori_mapnik_regioni_natura'),
    url(r'^nature/(?P<slug>[-\w]+)/province.xml$',
        MapnikProvinceView.as_view(filter='natura'), name='territori_mapnik_province_natura'),
)