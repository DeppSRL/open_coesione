from localita.models import Localita
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from vectorformats.Formats import Django, GeoJSON


class ProvinceListView(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        l = Localita.objects.filter(territorio='P')

        djf = Django.Django(geodjango="geom", properties=['nome', 'cod_prov'])
        geoj = GeoJSON.GeoJSON()
        return HttpResponse(geoj.encode(djf.decode(l)), mimetype='application/json')

class RegionListView(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        l = Localita.objects.filter(territorio='R')

        djf = Django.Django(geodjango="geom", properties=['nome', 'cod_reg'])
        geoj = GeoJSON.GeoJSON()
        return HttpResponse(geoj.encode(djf.decode(l)), mimetype='application/json')


class RegionDetailView(TemplateView):

    def render_to_response(self, context, **response_kwargs):
        params = context['params']
        cod_reg = params['cod_reg']
        type = params['type']
        if type != 'C' and type != 'P':
            raise Exception("Wrong type %s. C or P must be specified." % type)

        l = Localita.objects.filter(cod_reg=cod_reg, territorio=type)

        djf = Django.Django(geodjango="geom", properties=['nome', 'cod_prov', 'cod_com'])
        geoj = GeoJSON.GeoJSON()
        return HttpResponse(geoj.encode(djf.decode(l)), mimetype='application/json')


class ProvinceDetailView(TemplateView):

    def render_to_response(self, context, **response_kwargs):
        params = context['params']
        cod_prov = params['cod_prov']

        l = Localita.objects.filter(cod_prov=cod_prov, territorio='C')

        djf = Django.Django(geodjango="geom", properties=['nome', 'cod_com'])
        geoj = GeoJSON.GeoJSON()
        return HttpResponse(geoj.encode(djf.decode(l)), mimetype='application/json')

class MunicipalityDetailView(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        params = context['params']
        cod_com = params['cod_com']

        l = Localita.objects.filter(cod_com=cod_com)

        djf = Django.Django(geodjango="geom", properties=['nome'])
        geoj = GeoJSON.GeoJSON()
        return HttpResponse(geoj.encode(djf.decode(l)), mimetype='application/json')

