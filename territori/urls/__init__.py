from django.conf.urls import patterns, url, include
from territori.views import RegioneView, ComuneView, ProvinciaView, AmbitoNazionaleView, InfoView, TilesConfigView, AutocompleteView, TerritorioCSVView, AmbitoEsteroView

urlpatterns = patterns('',
    url(r'^regioni/(?P<slug>[-\w]+)/$', RegioneView.as_view(), name='territori_regione'),
    url(r'^province/(?P<slug>[-\w]+)/$', ProvinciaView.as_view(), name='territori_provincia'),
    url(r'^comuni/(?P<slug>[-\w]+)/$', ComuneView.as_view(), name='territori_comune'),
    url(r'^ambito-nazionale/$', AmbitoNazionaleView.as_view(), name='territori_nazionale'),
    url(r'^ambito-estero/$', AmbitoEsteroView.as_view(), name='territori_estero'),

    # csv comuni procapite per regioni
    url(r'^regioni/(?P<slug>[-\w]+).csv$', TerritorioCSVView.as_view(), name='progetti_regione_csv'),
    # csv comuni procapite per provincie
    url(r'^province/(?P<slug>[-\w]+).csv$', TerritorioCSVView.as_view(), name='progetti_provincia_csv'),

    url(r'^info/(?P<tipo>[\w]+)/(?P<lat>[-\d\.]+)/(?P<lng>[-\d\.]+)/$', InfoView.as_view(), name='territori_info'),
    url(r'^info/temi/(?P<slug>[-\w]+)/(?P<tipo>[\w]+)/(?P<lat>[-\d\.]+)/(?P<lng>[-\d\.]+)/$', InfoView.as_view(filter='temi'), name='territori_temi_info'),
    url(r'^info/nature/(?P<slug>[-\w]+)/(?P<tipo>[\w]+)/(?P<lat>[-\d\.]+)/(?P<lng>[-\d\.]+)/$', InfoView.as_view(filter='nature'), name='territori_nature_info'),
    url(r'^info/programmi/(?P<slug>[-\w]+)/(?P<tipo>[\w]+)/(?P<lat>[-\d\.]+)/(?P<lng>[-\d\.]+)/$', InfoView.as_view(filter='programmi'), name='territori_programmi_info'),
    url(r'^info/gruppo-programmi/(?P<slug>[-\w]+)/(?P<tipo>[\w]+)/(?P<lat>[-\d\.]+)/(?P<lng>[-\d\.]+)/$', InfoView.as_view(filter='gruppo_programmi'), name='territori_gruppoprogrammi_info'),

    url(r'^autocomplete/$', AutocompleteView.as_view(), name='territori_autocomplete'),
    url(r'^tiles.cfg$', TilesConfigView.as_view(), name='territori_tiles_cfg'),

    url(r'^mapnik/', include('territori.urls.mapnik')),
    url(r'^leaflet/', include('territori.urls.leaflet')),
)
