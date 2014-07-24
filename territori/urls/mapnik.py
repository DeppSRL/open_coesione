from django.conf import settings
from django.conf.urls import url, patterns
from django.views.decorators.cache import cache_page

from territori.views import MapnikRegioniView, MapnikProvinceView, MapnikComuniView

urlpatterns = patterns('',
    url(r'^regioni.xml$',
        MapnikRegioniView.as_view(inner_filter=None), name='territori_mapnik_regioni'),
    url(r'^province.xml$',
        MapnikProvinceView.as_view(inner_filter=None), name='territori_mapnik_province'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/province.xml$',
        MapnikProvinceView.as_view(inner_filter=None), name='territori_mapnik_province_regione'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/comuni.xml$',
        MapnikComuniView.as_view(inner_filter=None), name='territori_mapnik_comuni_regione'),
    url(r'^province/(?P<cod_prov>[\d]+)/comuni.xml$',
        MapnikComuniView.as_view(inner_filter=None), name='territori_mapnik_comuni_provincia'),
    url(r'^temi/(?P<slug>[-\w]+)/regioni.xml$',
        MapnikRegioniView.as_view(inner_filter='tema'), name='territori_mapnik_regioni_tema'),
    url(r'^temi/(?P<slug>[-\w]+)/province.xml$',
        MapnikProvinceView.as_view(inner_filter='tema'), name='territori_mapnik_province_tema'),
    url(r'^nature/(?P<slug>[-\w]+)/regioni.xml$',
        MapnikRegioniView.as_view(inner_filter='natura'), name='territori_mapnik_regioni_natura'),
    url(r'^nature/(?P<slug>[-\w]+)/province.xml$',
        MapnikProvinceView.as_view(inner_filter='natura'), name='territori_mapnik_province_natura'),
    url(r'^programmi/(?P<codice>[-\w]+)/regioni.xml$',
        MapnikRegioniView.as_view(inner_filter='programma'), name='territori_mapnik_regioni_programma'),
    url(r'^programmi/(?P<codice>[-\w]+)/province.xml$',
        MapnikProvinceView.as_view(inner_filter='programma'), name='territori_mapnik_province_programma'),
    url(r'^gruppo-programmi/(?P<slug>[-\w]+)/regioni.xml$',
        MapnikRegioniView.as_view(inner_filter='gruppo_programmi'), name='territori_mapnik_regioni_gruppoprogrammi'),
    url(r'^gruppo-programmi/(?P<slug>[-\w]+)/province.xml$',
        MapnikProvinceView.as_view(inner_filter='gruppo_programmi'), name='territori_mapnik_province_gruppoprogrammi'),
)