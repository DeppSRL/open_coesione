from django.conf.urls import url, patterns

from territori.views import LeafletRegioniView, LeafletProvinceView, LeafletComuniView

urlpatterns = patterns('',
    url(r'^regioni.xml$', LeafletRegioniView.as_view(filter=None), name='territori_leaflet_regioni'),
    url(r'^province.xml$', LeafletProvinceView.as_view(filter=None), name='territori_leaflet_province'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/province.xml$', LeafletProvinceView.as_view(filter=None), name='territori_leaflet_province_regione'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/comuni.xml$', LeafletComuniView.as_view(filter=None), name='territori_leaflet_comuni_regione'),
    url(r'^province/(?P<cod_pro>[\d]+)/comuni.xml$', LeafletComuniView.as_view(filter=None), name='territori_leaflet_comuni_provincia'),
    url(r'^temi/(?P<slug>[-\w]+)/regioni.xml$', LeafletRegioniView.as_view(filter='tema'), name='territori_leaflet_regioni_tema'),
    url(r'^temi/(?P<slug>[-\w]+)/province.xml$', LeafletProvinceView.as_view(filter='tema'), name='territori_leaflet_province_tema'),
    url(r'^nature/(?P<slug>[-\w]+)/regioni.xml$', LeafletRegioniView.as_view(filter='natura'), name='territori_leaflet_regioni_natura'),
    url(r'^nature/(?P<slug>[-\w]+)/province.xml$', LeafletProvinceView.as_view(filter='natura'), name='territori_leaflet_province_natura'),
)