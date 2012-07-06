from django.contrib.sites.models import Site
from django.db import models
from django.db.models.aggregates import Count, Sum
from django.template.defaultfilters import slugify
from django.http import HttpResponse, Http404
from django.contrib.gis.geos import Point
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.conf import settings
from open_coesione.views import AggregatoView
from open_coesione.data_classification import DataClassifier
from progetti.models import Progetto, Tema, ClassificazioneAzione
from territori.models import Territorio
import json
from lxml import etree
import re
import urllib


class JSONResponseMixin(object):
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(
            json.dumps(context),
            **response_kwargs
        )

class InfoView(JSONResponseMixin, TemplateView):
    """
    Returns the following info for a given point and location type:
    - denominazione
    - number, cost and payment for projects under that location (deep)
    Info are returned as JSON.

    This class can be used for an AJAX get request
    """
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(InfoView, self).get_context_data(**kwargs)
        tipo = context['params']['tipo']
        lat = float(context['params']['lat'])
        lon = float(context['params']['lng'])
        pnt = Point(lon, lat)
        territorio = Territorio.objects.get(geom__intersects=pnt, territorio=tipo)
        context['territorio'] = {
            'denominazione': territorio.denominazione,
            'n_progetti': territorio.progetti_deep.count(),
            'costo': float(territorio.progetti_deep.aggregate(s = Sum('fin_totale_pubblico'))['s']),
            'pagamento': float(territorio.progetti_deep.aggregate(s = Sum('pagamento'))['s']),
            }
        return context


class AutocompleteView(JSONResponseMixin, TemplateView):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AutocompleteView, self).get_context_data(**kwargs)
        query = self.request.GET['query']
        territori = Territorio.objects.filter(denominazione__istartswith=query).order_by('-popolazione_totale')[0:20]
        context['territori'] = [{
            'denominazione': territorio.nome_con_provincia,
            'url': territorio.get_absolute_url(),
            'id': territorio.pk
            } for territorio in territori]
        return context

class LeafletView(TemplateView):

    def get_template_names(self):
        """
        set template name according to extension
        extensions are validated at URL level
        """
        ext = self.kwargs['ext']
        if ext == 'html':
            return['territori/leaflet.html']
        else:
            return['territori/leaflet.js']

    def get_context_data(self, **kwargs):
        context = super(LeafletView, self).get_context_data(**kwargs)

        # fetch Geometry object to look at
        # - nation
        # - region
        # - province
        if 'cod_reg' in context['params']:
            codice = context['params']['cod_reg']
            area = Territorio.objects.get(territorio=Territorio.TERRITORIO.R, cod_reg=codice).geom
        elif 'cod_prov' in context['params']:
            codice = context['params']['cod_prov']
            area = Territorio.objects.get(territorio=Territorio.TERRITORIO.R, cod_prov=codice).geom
        else:
            area = Territorio.objects.filter(territorio=Territorio.TERRITORIO.R).collect()

        # compute bounds, to use inside the maps
        bounds = {
            'southwest': {
                'lng': str(area.extent[0]),
                'lat': str(area.extent[1])
            },
            'northeast': {
                'lng': str(area.extent[2]),
                'lat': str(area.extent[3])
            }
        }
        context['bounds'] = bounds

        # compute layer name from request.path and tematizzatione query string
        if 'tematizzazione' in self.request.GET:
            tematizzazione = self.request.GET['tematizzazione']
        else:
            tematizzazione = 'totale_costi'
        if tematizzazione not in ('totale_costi', 'totale_costi_pagati', 'totale_progetti'):
            raise Http404


        path = self.request.path.split(".")[0]
        context['layer_name'] = "_".join(path.split("/")[3:]) + "_" + tematizzazione

        # layer type may be R, P or C
        context['layer_type'] = path.split("/")[-1:][0][0:1].upper()

        # read legend html directly from mapnik xml (which should be cached at this point)
        mapnik_xml_path = "%s.xml?tematizzazione=%s" % (re.sub(r'leaflet', 'mapnik', path), tematizzazione)
        MAPNIK_HOST = settings.MAPNIK_HOST or Site.objects.get_current()
        mapnik_xml_url = "http://%s%s" % (MAPNIK_HOST, mapnik_xml_path)
        mapnik_xml = urllib.urlopen(mapnik_xml_url)
        tree = etree.parse(mapnik_xml, parser=etree.XMLParser())
        context['legend_html'] = tree.getroot()[0].text

        context['info_base_url'] = "http://{0}/territori/info".format(Site.objects.get_current())
        return context

class TilesConfigView(TemplateView):
    template_name = 'territori/tiles.cfg'

    def get_context_data(self, **kwargs):
        context = super(TilesConfigView, self).get_context_data(**kwargs)
        context['tematizzazioni'] = ('totale_costi', 'totale_costi_pagati', 'totale_progetti')
        context['regioni'] = Territorio.objects.filter(territorio='R')
        context['province'] = Territorio.objects.filter(territorio='P')
        context['mapnik_base_url'] = "http://{0}/territori/mapnik".format(Site.objects.get_current())

        return context

class MapnikView(TemplateView):
    """
    Base class for rendering xml Mapnik files
    """
    territori_name = 'Territori'
    template_name = 'territori/mapnik.xml'
    queryset = Territorio.objects.all()
    filter = None

    # Class-colors mapping
    colors = {
        'c0': '#eae7df',
        'c1': '#c9c7c3',
        'c2': '#969491',
        'c3': '#676462',
        'c4': '#2d2b2a',
    }

    def get_context_data(self, **kwargs):
        context = super(MapnikView, self).get_context_data(**kwargs)
        context['territori_name'] = self.territori_name
        context['codice_field'] = self.codice_field
        context['srs'] = self.srs
        context['shp_file'] = self.shp_file
        context['countries_shp_file'] = '{0}/dati/countries/82945364-10m-admin-0-countries.shp'.format(settings.REPO_ROOT)

        self.refine_context(context)

        # compute all costi, to be used in classification
        # 'n_progetti': t.progetti_deep.count(),
        # 'pagamenti': t.progetti_deep.aggregate(s=Sum('pagamento'))['s']

        if 'tematizzazione' in self.request.GET:
            tematizzazione = self.request.GET['tematizzazione']
        else:
            tematizzazione = 'totale_costi'
        if tematizzazione not in ('totale_costi', 'totale_costi_pagati', 'totale_progetti'):
            raise Http404

        data = {}
        for t in self.queryset:
            data[t.codice] = float(getattr(Progetto.objects, tematizzazione)(territorio=t))

        # DataClassifier instance
        self.dc = DataClassifier(data.values(), classifier_args={'k': 5}, colors_map=self.colors)
        context['classification_bins'] = self.dc.get_bins_ranges()



        # return codice and colore, for each territorio
        # to be easily used in the view
        context['territori'] = []
        for t in self.queryset:
            colore = self.dc.get_color(data[t.codice])

            context['territori'].append({
                'codice': t.codice,
                'colore': colore,
            })

        return context

    def refine_context(self, context):
        pass


class MapnikRegioniView(MapnikView):
    territori_name = 'regioni'
    codice_field = 'COD_REG'
    srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
    shp_file = '{0}/dati/reg2011_g/regioni_stats.shp'.format(settings.REPO_ROOT)
    queryset = Territorio.objects.filter(territorio='R')

    def refine_context(self, context):
        pass


class MapnikProvinceView(MapnikView):
    territori_name = 'province'
    codice_field = 'COD_PRO'
    srs = "+proj=utm +zone=32 +ellps=intl +units=m +no_defs"
    shp_file = '{0}/dati/prov2011_g/prov2011_g.shp'.format(settings.REPO_ROOT)

    def refine_context(self, context):
        if 'cod_reg' in context['params']:
            cod_reg = context['params']['cod_reg']
            self.queryset = Territorio.objects.filter(territorio='P', cod_reg=cod_reg)
            self.territori_name = 'regioni_%s_province' % cod_reg
        else:
            self.queryset = Territorio.objects.filter(territorio='P')


class MapnikComuniView(MapnikView):
    territori_name = 'comuni'
    codice_field = 'PRO_COM'
    srs = "+proj=utm +zone=32 +ellps=intl +units=m +no_defs"
    shp_file = '{0}/dati/com2011_g/com2011_g.shp'.format(settings.REPO_ROOT)

    def refine_context(self, context):
        if 'cod_reg' in context['params']:
            cod_reg = context['params']['cod_reg']
            self.queryset = Territorio.objects.filter(territorio='C', cod_reg=cod_reg)
            self.territori_name = 'regioni_%s_comuni' % cod_reg
        elif 'cod_prov' in context['params']:
            cod_prov = context['params']['cod_prov']
            self.queryset = Territorio.objects.filter(territorio='C', cod_prov=cod_prov)
            self.territori_name = 'province_%s_comuni' % cod_prov
        else:
            raise Exception("a region or a province must be specified for this view")


class TerritorioView(AggregatoView, DetailView):
    context_object_name = 'territorio'
    tipo_territorio = ''
    model = 'Territorio'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TerritorioView, self).get_context_data(**kwargs)

        context['total_cost'] = Progetto.objects.totale_costi(territorio=self.object)
        context['total_cost_paid'] = Progetto.objects.totale_costi_pagati(territorio=self.object)
        context['total_projects'] = Progetto.objects.totale_progetti(territorio=self.object)
        context['total_allocated_resources'] = Progetto.objects.totale_risorse_stanziate(territorio=self.object)
        context['cost_payments_ratio'] = "{0:.0%}".format(context['total_cost_paid'] / context['total_cost'] if context['total_cost'] > 0.0 else 0.0)

        context['temi_principali'] = [
            {
            'object': tema,
            'data': Tema.objects.\
                filter(tema_superiore=tema).\
                filter(**self.object.get_cod_dict(prefix='progetto_set__territorio_set__')).\
                aggregate(numero=Count('progetto_set'),
                          costo=Sum('progetto_set__fin_totale_pubblico'),
                          pagamento=Sum('progetto_set__pagamento'))
            } for tema in Tema.objects.principali()
        ]

        context['tipologie_principali'] = [
            {
            'object': natura,
            'data': ClassificazioneAzione.objects.\
                filter(classificazione_superiore=natura).\
                filter(**self.object.get_cod_dict(prefix='progetto_set__territorio_set__')).\
                aggregate(numero=Count('progetto_set'),
                          costo=Sum('progetto_set__fin_totale_pubblico'),
                          pagamento=Sum('progetto_set__pagamento'))
            } for natura in ClassificazioneAzione.objects.tematiche()
        ]

        context['top_progetti_per_costo'] = Progetto.objects.nel_territorio(self.object).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]
        context['ultimi_progetti_conclusi'] = Progetto.objects.conclusi().nel_territorio(self.object)[:5]

        context['territori_piu_finanziati_pro_capite'] = Territorio.objects\
            .filter( territorio=Territorio.TERRITORIO.C ,**self.object.get_cod_dict() )\
            .exclude(pk=self.object.pk)\
            .annotate( totale=models.Sum('progetto__fin_totale_pubblico') )\
            .filter( totale__isnull=False )\
            .order_by('-totale')[:5]
        # sotto territori del territorio richiesto
#        context['territori_piu_finanziati'] = Territorio.objects\
#                .exclude(pk=self.object.pk)\
#                .filter(totale__isnull=False, territorio= Territorio.TERRITORIO.C, **self.object.get_cod_dict())\
#                .annotate(totale=models.Sum('progetto__costo'))\
#                .order_by('-fin_totale_pubblico')[:3]

        context['map'] = self.get_map_context( self.object )

        return context

    def get_object(self, queryset=None):
        return Territorio.objects.get(slug= slugify(self.kwargs['slug']) , territorio= self.tipo_territorio)


class RegioneView(TerritorioView):
    tipo_territorio = Territorio.TERRITORIO.R

class ProvinciaView(TerritorioView):
    tipo_territorio = Territorio.TERRITORIO.P

class ComuneView(TerritorioView):
    tipo_territorio = Territorio.TERRITORIO.C