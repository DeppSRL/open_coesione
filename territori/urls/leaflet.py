from django.conf import settings
from django.conf.urls import url, patterns
from django.views.decorators.cache import cache_page
from territori.views import LeafletView

urlpatterns = patterns('',
    url(r'^world.(?P<ext>(json|html))$',
        LeafletView.as_view(layer='world'), name='territori_leaflet_world'),
    url(r'^regioni.(?P<ext>(json|html))$',
        LeafletView.as_view(), name='territori_leaflet_regioni'),
    url(r'^province.(?P<ext>(json|html))$',
        LeafletView.as_view(), name='territori_leaflet_province'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/province.(?P<ext>(json|html))$',
        LeafletView.as_view(), name='territori_leaflet_province_regione'),
    url(r'^regioni/(?P<cod_reg>[\d]+)/comuni.(?P<ext>(json|html))$',
        LeafletView.as_view(), name='territori_leaflet_comuni_regione'),
    url(r'^province/(?P<cod_prov>[\d]+)/comuni.(?P<ext>(json|html))$',
        LeafletView.as_view(), name='territori_leaflet_comuni_provincia'),
    url(r'^temi/(?P<slug>[-\w]+)/regioni.(?P<ext>(json|html))$',
        LeafletView.as_view(inner_filter='tema'), name='territori_leaflet_regioni_tema'),
    url(r'^temi/(?P<slug>[-\w]+)/province.(?P<ext>(json|html))$',
        LeafletView.as_view(inner_filter='tema'), name='territori_leaflet_province_tema'),
    url(r'^nature/(?P<slug>[-\w]+)/regioni.(?P<ext>(json|html))$',
        LeafletView.as_view(inner_filter='natura'), name='territori_leaflet_regioni_natura'),
    url(r'^nature/(?P<slug>[-\w]+)/province.(?P<ext>(json|html))$',
        LeafletView.as_view(inner_filter='natura'), name='territori_leaflet_province_natura'),
    url(r'^programmi/(?P<codice>[\w]+)/regioni.(?P<ext>(json|html))$',
        LeafletView.as_view(inner_filter='programma'), name='territori_leaflet_regioni_programma'),
    url(r'^programmi/(?P<codice>[\w]+)/province.(?P<ext>(json|html))$',
        LeafletView.as_view(inner_filter='programma'), name='territori_leaflet_province_programma'),
)