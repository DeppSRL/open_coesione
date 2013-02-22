from django.views.decorators.cache import cache_page
from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView
from territori.views import RegioneView, ComuneView, ProvinciaView, AmbitoNazionaleView, InfoView, TilesConfigView, AutocompleteView, RegioneCSVView, ProvinciaCSVView, AmbitoEsteroView


class ChartView(TemplateView):
    template_name = 'territori/index_chart.html'

    def get_context_data(self, **kwargs):
        from progetti.models import Tema
        from territori.models import Territorio
        return {
            'params': kwargs,
            'temi_principali': Tema.objects.principali(),
            'tema': Tema.objects.get(codice=self.request.GET.get('tema', '1')),
            'regioni': Territorio.objects.regioni(),
            'territorio': Territorio.objects.get(cod_reg=self.request.GET.get('regione', '1'), territorio='R'),
        }

urlpatterns = patterns('',
    url(r'^regioni/(?P<slug>[-\w]+)/$', RegioneView.as_view(), name='territori_regione'),
    # csv comuni procapite per regioni
    url(r'^regioni/(?P<slug>[-\w]+).csv$', RegioneCSVView.as_view(), name='progetti_regione_csv'),

    url(r'^province/(?P<slug>[-\w]+)/$', ProvinciaView.as_view(), name='territori_provincia'),
    # csv comuni procapite per provincie
    url(r'^regioni/(?P<slug>[-\w]+).csv$', ProvinciaCSVView.as_view(), name='progetti_provincia_csv'),
    url(r'^comuni/(?P<slug>[-\w]+)/$', ComuneView.as_view(), name='territori_comune'),
    url(r'^ambito-nazionale/$', AmbitoNazionaleView.as_view(), name='territori_nazionale'),
    url(r'^ambito-estero/$', AmbitoEsteroView.as_view(), name='territori_estero'),

    url(r'^info/(?P<tipo>[\w]+)/(?P<lat>[-\d\.]+)/(?P<lng>[-\d\.]+)/$',
       cache_page(key_prefix='info')(InfoView.as_view()), name='territori_info'),
    url(r'^info/temi/(?P<slug>[-\w]+)/(?P<tipo>[\w]+)/(?P<lat>[-\d\.]+)/(?P<lng>[-\d\.]+)/$',
        cache_page(key_prefix='info_temi')(InfoView.as_view(filter='temi')), name='territori_temi_info'),
    url(r'^info/nature/(?P<slug>[-\w]+)/(?P<tipo>[\w]+)/(?P<lat>[-\d\.]+)/(?P<lng>[-\d\.]+)/$',
        cache_page(key_prefix='info_nature')(InfoView.as_view(filter='nature')), name='territori_nature_info'),
    url(r'^autocomplete/$',
        AutocompleteView.as_view(), name='territori_autocomplete'),
    url(r'^tiles.cfg$', TilesConfigView.as_view(), name='territori_tiles_cfg'),
    url(r'^mapnik/', include('territori.urls.mapnik')),
    url(r'^leaflet/', include('territori.urls.leaflet')),
    url(r'^charts.html$', ChartView.as_view(), name='territori_charts'),


)
