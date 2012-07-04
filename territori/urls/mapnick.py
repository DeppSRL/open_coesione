from django.conf.urls import url, patterns

from territori.views import MapnickRegioniView, MapnickProvinceView, MapnickComuniView

urlpatterns = patterns('',
    url(r'^regioni.xml$', MapnickRegioniView.as_view(filter=None), name='territori_mapnick_regioni'),
    url(r'^province.xml$', MapnickProvinceView.as_view(filter=None), name='territori_mapnick_province'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/province.xml$', MapnickProvinceView.as_view(filter=None), name='territori_mapnick_province_regione'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/comuni.xml$', MapnickComuniView.as_view(filter=None), name='territori_mapnick_comuni_regione'),
    url(r'^province/(?P<cod_pro>[\d]+)/comuni.xml$', MapnickComuniView.as_view(filter=None), name='territori_mapnick_comuni_provincia'),
    url(r'^temi/(?P<slug>[-\w]+)/regioni.xml$', MapnickRegioniView.as_view(filter='tema'), name='territori_mapnick_regioni_tema'),
    url(r'^temi/(?P<slug>[-\w]+)/province.xml$', MapnickProvinceView.as_view(filter='tema'), name='territori_mapnick_province_tema'),
    url(r'^nature/(?P<slug>[-\w]+)/regioni.xml$', MapnickRegioniView.as_view(filter='natura'), name='territori_mapnick_regioni_natura'),
    url(r'^nature/(?P<slug>[-\w]+)/province.xml$', MapnickProvinceView.as_view(filter='natura'), name='territori_mapnick_province_natura'),
)