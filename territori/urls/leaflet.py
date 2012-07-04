from django.conf.urls import url, patterns
from territori.views import LeafletView

urlpatterns = patterns('',
    url(r'^regioni$', LeafletView.as_view(), name='territori_leaflet_regioni'),
    url(r'^province$', LeafletView.as_view(), name='territori_leaflet_province'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/province$', LeafletView.as_view(), name='territori_leaflet_province_regione'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/comuni$', LeafletView.as_view(), name='territori_leaflet_comuni_regione'),
    url(r'^province/(?P<cod_pro>[\d]+)/comuni$', LeafletView.as_view(), name='territori_leaflet_comuni_provincia'),
    url(r'^temi/(?P<slug>[-\w]+)/regioni$', LeafletView.as_view(), name='territori_leaflet_regioni_tema'),
    url(r'^temi/(?P<slug>[-\w]+)/province$', LeafletView.as_view(), name='territori_leaflet_province_tema'),
    url(r'^nature/(?P<slug>[-\w]+)/regioni$', LeafletView.as_view(), name='territori_leaflet_regioni_natura'),
    url(r'^nature/(?P<slug>[-\w]+)/province$', LeafletView.as_view(), name='territori_leaflet_province_natura'),
)