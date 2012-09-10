from django.contrib.sites.models import Site
from django.db import models
from django.template.defaultfilters import slugify
from django.http import HttpResponse, Http404
from django.contrib.gis.geos import Point
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.conf import settings
from open_coesione import utils
from open_coesione.data_classification import DataClassifier
from open_coesione.views import AccessControlView, AggregatoView
from progetti.models import Progetto, Tema, ClassificazioneAzione
from progetti.views import CSVView
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

    filter = None

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(InfoView, self).get_context_data(**kwargs)
        tipo = kwargs['tipo']
        lat = float(kwargs['lat'])
        lon = float(kwargs['lng'])
        pnt = Point(lon, lat)

        try:
            territorio = Territorio.objects.get(geom__intersects=pnt, territorio=tipo)
        except Territorio.DoesNotExist:
            return { 'success' : False }

        context['success'] = True

        territorio_hierarchy = territorio.get_hierarchy()


        territori = territorio.get_breadcrumbs()

        tema = None
        if self.filter == 'temi':
            tema = Tema.objects.get(slug=kwargs['slug'])
            territori = [(t.denominazione, t.get_progetti_search_url(tema=tema))
                          for t in territorio_hierarchy]

        natura = None
        if self.filter == 'nature':
            natura = ClassificazioneAzione.objects.get(slug=kwargs['slug'])
            territori = [(t.denominazione, t.get_progetti_search_url(natura=natura))
                        for t in territorio_hierarchy]

        popolazione_totale = (territorio.popolazione_totale if territorio else Territorio.objects.nazione().popolazione_totale) or 0
        costo_totale = Progetto.objects.totale_costi(territorio=territorio, tema=tema, classificazione=natura) or 0

        context['territorio'] = {
            'denominazione': territorio.denominazione,
            'n_progetti': Progetto.objects.totale_progetti(territorio=territorio, tema=tema, classificazione=natura) or 0,
            'costo': costo_totale,
            'costo_procapite': costo_totale / popolazione_totale if popolazione_totale else '',
            'pagamento': Progetto.objects.totale_pagamenti(territorio=territorio, tema=tema, classificazione=natura) or 0,
            'territori': territori
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
            'id': territorio.pk,
            'cod_com': territorio.cod_com,
            'cod_prov': territorio.cod_prov,
            'cod_reg': territorio.cod_reg,
        } for territorio in territori]
        return context


class LeafletView(TemplateView):
    template_name = 'territori/leaflet.html'
    filter = None
    layer = None

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        if self.kwargs['ext'] == 'json':
            response_kwargs['content_type'] = 'application/json'
            context['tilestache_url'] = settings.TILESTACHE_URL
            return HttpResponse(
                json.dumps(context),
                **response_kwargs
            )

        return self.response_class(
            request = self.request,
            template = self.get_template_names(),
            context = context,
            **response_kwargs
        )

    def get_context_data(self, **kwargs):
        context = super(LeafletView, self).get_context_data(**kwargs)

        # fetch Geometry object to look at
        # - nation
        # - region
        # - province
        if 'cod_reg' in context['params']:
            codice = context['params']['cod_reg']
            area = Territorio.objects.get(territorio=Territorio.TERRITORIO.R, cod_reg=codice).geom
            context['zoom'] = { 'min' : 7, 'max' : 10 }
        elif 'cod_prov' in context['params']:
            codice = context['params']['cod_prov']
            area = Territorio.objects.get(territorio=Territorio.TERRITORIO.P, cod_prov=codice).geom
            context['zoom'] = { 'min' : 8, 'max' : 11 }
        else:
            # Collect all comuni except 'Lampedusa e Linosa' to reduce zoomlevel of fitbound
            area = Territorio.objects.filter(territorio=Territorio.TERRITORIO.C).exclude(cod_com='84020').collect()
            context['zoom'] = { 'min' : 5, 'max' : 7 }

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

        if self.layer == 'world':
            context['zoom'] = { 'min' : 4, 'max' : 11 }
            context['layer_name'] = 'world'
            return context

        # compute layer name from request.path and tematizzatione query string
        if 'tematizzazione' in self.request.GET:
            tematizzazione = self.request.GET['tematizzazione']
        else:
            tematizzazione = 'totale_costi'
        if tematizzazione not in TilesConfigView.TEMATIZZAZIONI:
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

        # info_base_url for popup changes in case temi or nature filters are applied
        if self.filter:
            context['info_base_url'] = "/territori/info/{0}/{1}".format(
                #Site.objects.get_current(),
                self.filter, self.kwargs['slug']
            )
        else:
            context['info_base_url'] = "/territori/info".format(Site.objects.get_current())
        return context

class TilesConfigView(TemplateView):
    template_name = 'territori/tiles.cfg'

    TEMATIZZAZIONI = (
        'totale_costi', 'totale_pagamenti', 'totale_progetti',
        'totale_costi_procapite', 'totale_pagamenti_procapite', 'totale_progetti_procapite')

    def get_context_data(self, **kwargs):
        context = super(TilesConfigView, self).get_context_data(**kwargs)
        context['tematizzazioni'] = self.TEMATIZZAZIONI
        context['regioni'] = Territorio.objects.filter(territorio='R')
        context['province'] = Territorio.objects.filter(territorio='P')
        context['temi'] = Tema.objects.principali()
        context['nature'] = ClassificazioneAzione.objects.nature()
        context['mapnik_base_url'] = "http://{0}/territori/mapnik".format(Site.objects.get_current())
        context['path_to_cache'] = settings.TILESTACHE_CACHE_PATH

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
    colors = settings.MAP_COLORS

    # Manager for Progetti
    manager = Progetto.objects

    def get_context_data(self, **kwargs):
        context = super(MapnikView, self).get_context_data(**kwargs)
        context['territori_name'] = self.territori_name
        context['codice_field'] = self.codice_field
        context['srs'] = self.srs
        context['shp_file'] = self.shp_file
        context['countries_shp_file'] = '{0}/dati/countries/82945364-10m-admin-0-countries.shp'.format(settings.REPO_ROOT)

        self.refine_context(context)

        # get tematisation from GET
        # totale_costi is the default tematisation
        # tematizzazione contains the name of the method in progetti.managers.ProgettiManager
        if 'tematizzazione' in self.request.GET:
            tematizzazione = self.request.GET['tematizzazione']
        else:
            tematizzazione = 'totale_costi'
        if tematizzazione not in TilesConfigView.TEMATIZZAZIONI:
            raise Http404

        # build the collection of aggregated data for the map
        data = {}

        # eventual filter on tema
        tema = None
        if self.filter == 'tema':
            tema = Tema.objects.get(slug=self.kwargs['slug'])

        # eventual filter on natura
        natura = None
        if self.filter == 'natura':
            natura = ClassificazioneAzione.objects.get(slug=self.kwargs['slug'])

        # loop over all territories
        # foreach, invoke the tematizzazione method, with specified filters
        for t in self.queryset:
            #data[t.codice] = float(getattr(self.manager, tematizzazione)(territorio=t))
            data[t.codice] = getattr(Progetto.objects, tematizzazione)(
                    territorio=t,
                    tema=tema,
                    classificazione=natura
            )

        # DataClassifier instance
        self.dc = DataClassifier(data.values(), classifier_args={'k': 5}, colors_map=self.colors)
        context['classification_bins'] = self.dc.get_bins_ranges()



        # return codice and colore, for each territorio
        # to be easily used in the view
        context['territori'] = []
        for t in self.queryset:
            colore = self.dc.get_color(data[t.codice])

            context['territori'].append({
                'codice': str(t.codice),
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
        #super(MapnikProvinceView, self).refine_context(context)
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
        #super(MapnikComuniView, self).refine_context(context)
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


class TerritorioView(AccessControlView, AggregatoView, DetailView):
    context_object_name = 'territorio'
    tipo_territorio = ''
    model = 'Territorio'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TerritorioView, self).get_context_data(**kwargs)

        context = self.get_aggregate_data(context, territorio=self.object)

        context['top_progetti_per_costo'] = Progetto.objects.nel_territorio(self.object).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]
        context['ultimi_progetti_conclusi'] = Progetto.objects.conclusi().nel_territorio(self.object)[:5]

        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(
            filters=self.object.get_cod_dict()
        )

        return context

    def get_object(self, queryset=None):
        return (Territorio.objects.get(slug= slugify(self.kwargs['slug']) , territorio= self.tipo_territorio)
            if 'slug' in self.kwargs
            else Territorio.objects.get(territorio= self.tipo_territorio))


class RegioneView(TerritorioView):
    tipo_territorio = Territorio.TERRITORIO.R

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RegioneView, self).get_context_data(**kwargs)

        try:
            context['popolazione_nazionale'] = Territorio.objects.nazione().popolazione_totale
        except (Territorio.DoesNotExist, Territorio.MultipleObjectsReturned) :
            pass

        return context


class ProvinciaView(TerritorioView):
    tipo_territorio = Territorio.TERRITORIO.P

class ComuneView(TerritorioView):
    tipo_territorio = Territorio.TERRITORIO.C

class AmbitoNazionaleView(TerritorioView):
    tipo_territorio = Territorio.TERRITORIO.N

class RegioneCSVView(CSVView):
    model = Territorio

    def write_csv(self, response):
        territorio_filter = self.object.get_cod_dict()
        writer = utils.UnicodeWriter(response)
        writer.writerow( self.get_first_row() )
        comuni = list(Territorio.objects.comuni().filter(**territorio_filter))
        provincie = dict([(t['cod_prov'], t['denominazione']) for t in Territorio.objects.provincie().filter(**territorio_filter).values('cod_prov','denominazione')])
        comuni_con_pro_capite = self.top_comuni_pro_capite(territorio_filter, qnt=None)

        for city in comuni_con_pro_capite:
            writer.writerow([
                unicode(city.denominazione),
                unicode(provincie[city.cod_prov]),
                '{0:.2f}'.format( city.totale / city.popolazione_totale if city in comuni_con_pro_capite else .0).replace('.', ',')
            ])
            comuni.remove(city)

        for city in comuni:
            writer.writerow([
                unicode(city.denominazione),
                unicode(provincie[city.cod_prov]),
                '{0:.2f}'.format( .0 ).replace('.', ',')
            ])

class ProvinciaCSVView(RegioneCSVView):


    def write_csv(self, response):
        territorio_filter = self.object.get_cod_dict()
        writer = utils.UnicodeWriter(response)
        writer.writerow( self.get_first_row() )
        comuni = list(Territorio.objects.comuni().filter(**territorio_filter))

        comuni_con_pro_capite = self.top_comuni_pro_capite(territorio_filter, qnt=None)

        for city in comuni_con_pro_capite:
            writer.writerow([
                unicode(city.denominazione),
                unicode(self.object.denominazione),
                '{0:.2f}'.format( city.totale / city.popolazione_totale if city in comuni_con_pro_capite else .0).replace('.', ',')
            ])
            comuni.remove(city)

        for city in comuni:
            writer.writerow([
                unicode(city.denominazione),
                unicode(self.object.denominazione),
                '{0:.2f}'.format( .0 ).replace('.', ',')
            ])