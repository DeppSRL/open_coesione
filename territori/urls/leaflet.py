from django.conf.urls import url, patterns
from territori.views import LeafletView

urlpatterns = patterns('',
    url(r'^regioni.(?P<ext>(js|html))$', LeafletView.as_view(), name='territori_leaflet_regioni'),
    url(r'^province.(?P<ext>(js|html))$', LeafletView.as_view(), name='territori_leaflet_province'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/province.(?P<ext>(js|html))$', LeafletView.as_view(), name='territori_leaflet_province_regione'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/comuni.(?P<ext>(js|html))$', LeafletView.as_view(), name='territori_leaflet_comuni_regione'),
    url(r'^province/(?P<cod_pro>[\d]+)/comuni.(?P<ext>(js|html))$', LeafletView.as_view(), name='territori_leaflet_comuni_provincia'),
    url(r'^temi/(?P<slug>[-\w]+)/regioni.(?P<ext>(js|html))$', LeafletView.as_view(), name='territori_leaflet_regioni_tema'),
    url(r'^temi/(?P<slug>[-\w]+)/province.(?P<ext>(js|html))$', LeafletView.as_view(), name='territori_leaflet_province_tema'),
    url(r'^nature/(?P<slug>[-\w]+)/regioni.(?P<ext>(js|html))$', LeafletView.as_view(), name='territori_leaflet_regioni_natura'),
    url(r'^nature/(?P<slug>[-\w]+)/province.(?P<ext>(js|html))$', LeafletView.as_view(), name='territori_leaflet_province_natura'),
)