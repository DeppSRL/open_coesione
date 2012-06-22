from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from territori.views import RegioneView, ComuneView, ProvinciaView

class ChartView(TemplateView):
    template_name='territori/index_chart.html'

    def get_context_data(self, **kwargs):
        from progetti.models import Tema
        from territori.models import Territorio
        return {
            'params': kwargs,
            'temi_principali': Tema.objects.principali(),
            'tema': Tema.objects.get(codice=self.request.GET.get('tema','1') ),
            'regioni': Territorio.objects.regioni(),
            'territorio': Territorio.objects.get(cod_reg=self.request.GET.get('regione','1'), territorio='R'),
        }

urlpatterns = patterns('',
    url(r'^regioni/(?P<slug>[-\w]+)/$',
       RegioneView.as_view(), name='territori_regione'),
    url(r'^province/(?P<slug>[-\w]+)/$',
       ProvinciaView.as_view(), name='territori_provincia'),
    url(r'^comuni/(?P<slug>[-\w]+)/$',
       ComuneView.as_view(), name='territori_comune'),
    url(r'^polymaps.html$', TemplateView.as_view(template_name='territori/polymaps.html'), name='territori_polymaps'),
    url(r'^highcharts.html$', TemplateView.as_view(template_name='territori/highcharts.html'), name='territori_highcharts'),
    url(r'^charts.html$', ChartView.as_view(), name='territori_highcharts'),
)