from localita.models import Localita
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from vectorformats.Formats import Django, GeoJSON


class RegionListView(TemplateView):
    def render_to_response(self, context, **response_kwargs):

        l = Localita.objects.filter(territorio='R')

        djf = Django.Django(geodjango="geom", properties=['denominazione'])
        geoj = GeoJSON.GeoJSON()
        return HttpResponse(geoj.encode(djf.decode(l)), mimetype='application/json')


class RegionDetailView(TemplateView):

    def render_to_response(self, context, **response_kwargs):

        params = context['params']
        cod_reg = params['cod_reg']
        l = Localita.objects.filter(cod_reg=cod_reg, territorio='C')

        djf = Django.Django(geodjango="geom", properties=['denominazione', 'denominazione_ted'])
        geoj = GeoJSON.GeoJSON()
        return HttpResponse(geoj.encode(djf.decode(l)), mimetype='application/json')

