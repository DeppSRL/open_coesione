from django.db.models.aggregates import Count
from localita.models import Localita
from localita import getTilesConfig

from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse
from vectorformats.Formats import Django, GeoJSON

import TileStache

class ProvinceListView(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        l = Localita.objects.filter(territorio='P')

        djf = Django.Django(geodjango="geom", properties=['nome', 'cod_prov', 'n_progetti_deep'])
        geoj = GeoJSON.GeoJSON()
        return HttpResponse(geoj.encode(djf.decode(l)), mimetype='application/json')

class RegionListView(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        l = Localita.objects.filter(territorio='R')

        djf = Django.Django(geodjango="geom", properties=['nome', 'cod_reg', 'n_progetti_deep'])
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

        djf = Django.Django(geodjango="geom", properties=['nome', 'cod_prov', 'cod_com', 'n_progetti_deep'])
        geoj = GeoJSON.GeoJSON()
        return HttpResponse(geoj.encode(djf.decode(l)), mimetype='application/json')


class ProvinceDetailView(TemplateView):

    def render_to_response(self, context, **response_kwargs):
        params = context['params']
        cod_prov = params['cod_prov']

        l = Localita.objects.filter(cod_prov=cod_prov, territorio='C')

        djf = Django.Django(geodjango="geom", properties=['nome', 'cod_com', 'n_progetti_deep'])
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


class TilesView(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        """
        Proxy to tilestache
        {X} - coordinate column.
        {Y} - coordinate row.
        {B} - bounding box.
        {Z} - zoom level.
        {S} - host.
        """
        params = context['params']
        layer_name = params['layer_name']
        z = params['z']
        x = params['x']
        y = params['y']
        extension = params['extension']

        config = getTilesConfig()
        path_info = "%s/%s/%s/%s.%s" % (layer_name, z, x, y, extension)
        coord, extension = TileStache.splitPathInfo(path_info)[1:]

        mimetype, content = TileStache.getTile(config.layers[layer_name], coord, extension)
        return HttpResponse(content, mimetype=mimetype)

class PolymapsView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(PolymapsView, self).get_context_data(**kwargs)
        config = getTilesConfig()
        layer_urls = []
        for l in config.layers:
            if isinstance(config.layers[l].provider, TileStache.Providers.Vector.Provider):
                layer_urls.append(reverse('tiles_url', args=[l, '{Z}', '{X}', '{Y}', 'geojson']).replace('%7B', '{').replace('%7D', '}'))
        context['layer_urls'] = layer_urls
        return context
