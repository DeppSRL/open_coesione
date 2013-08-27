from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Count
from django.template.defaultfilters import slugify
from django.http import HttpResponse, Http404
from django.contrib.gis.geos import Point
from django.views.generic import ListView
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.conf import settings
from django.core.cache import cache
from open_coesione import utils
from open_coesione.data_classification import DataClassifier
from open_coesione.views import AccessControlView, AggregatoView, cached_context
from progetti.models import Progetto, Tema, ClassificazioneAzione, ProgrammaAsseObiettivo
from progetti.views import CSVView
from territori.models import Territorio

import json
from lxml import etree
import re
import urllib
import logging

logger = logging.getLogger('oc')


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
            return {'success': False}

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

        programma = None
        if self.filter == 'programmi':
            programma = ProgrammaAsseObiettivo.objects.get(codice=kwargs['slug'])
            territori = [(t.denominazione, t.get_progetti_search_url(programma=programma))
                        for t in territorio_hierarchy]

        # prepare the cache key
        tema_key = tema.slug if tema is not None else 'na'
        natura_key = natura.slug if natura is not None else 'na'
        programma_key = programma.codice if programma is not None else 'na'
        cache_key = "terr:{0}_tema:{1}_natura:{2}_programma:{3}".format(
            territorio.pk,
            tema_key, natura_key, programma_key
        )

        # check vars existance in the cache, or compute and store them
        cached_vars = cache.get(cache_key)
        if cached_vars is None:
            cached_vars = {
                'popolazione_totale': (territorio.popolazione_totale if territorio else Territorio.objects.nazione().popolazione_totale) or 0,
                'costo_totale': Progetto.objects.totale_costi(territorio=territorio, tema=tema, classificazione=natura, programma=programma) or 0,
                'n_progetti': Progetto.objects.totale_progetti(territorio=territorio, tema=tema, classificazione=natura, programma=programma) or 0,
                'pagamento_totale': Progetto.objects.totale_pagamenti(territorio=territorio, tema=tema, classificazione=natura, programma=programma) or 0,
            }
            cache.set(cache_key, cached_vars)

        # extract cached vars to local variables for code-readability
        n_progetti = cached_vars['n_progetti']
        costo_totale = cached_vars['costo_totale']
        pagamento_totale = cached_vars['pagamento_totale']
        popolazione_totale = cached_vars['popolazione_totale']

        # modify context
        context['territorio'] = {
            'denominazione': territorio.denominazione,
            'n_progetti': n_progetti,
            'costo': costo_totale,
            'costo_procapite': costo_totale / popolazione_totale if popolazione_totale else '',
            'pagamento': pagamento_totale,
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
    inner_filter = None
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

    @cached_context
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

        # info_base_url for popup changes in case temi, nature or programmi filters are applied
        if self.inner_filter:
            if 'slug' in self.kwargs:
                pk = self.kwargs['slug']
            elif 'codice' in self.kwargs:
                pk = self.kwargs['codice']
            else:
                raise Exception('slug or codice must be in kwargs')

            filter_plurals = {
                'tema': 'temi',
                'natura': 'nature',
                'programma': 'programmi',
            }

            # convert inner_filter to its plural when creating info url
            context['info_base_url'] = "/territori/info/{0}/{1}".format(
                filter_plurals[self.inner_filter],
                pk
            )
        else:
            context['info_base_url'] = "/territori/info".format(Site.objects.get_current())
        return context


class TilesConfigView(TemplateView):
    template_name = 'territori/tiles.cfg'

    TEMATIZZAZIONI = (
        'totale_costi', 'totale_pagamenti', 'totale_progetti',
        'totale_costi_procapite')

    def get_context_data(self, **kwargs):
        context = super(TilesConfigView, self).get_context_data(**kwargs)
        context['tematizzazioni'] = self.TEMATIZZAZIONI
        context['regioni'] = Territorio.objects.filter(territorio='R')
        context['province'] = Territorio.objects.filter(territorio='P')
        context['temi'] = Tema.objects.principali()
        context['nature'] = ClassificazioneAzione.objects.nature()
        context['programmi'] = ProgrammaAsseObiettivo.objects.programmi()
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
    inner_filter = None

    # Class-colors mapping
    colors = settings.MAP_COLORS

    # Manager for Progetti
    manager = Progetto.objects

    @cached_context
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
        nonzero_data = {}

        # eventual filter on tema
        tema = None
        if self.inner_filter == 'tema':
            tema = Tema.objects.get(slug=self.kwargs['slug'])

        # eventual filter on natura
        natura = None
        if self.inner_filter == 'natura':
            natura = ClassificazioneAzione.objects.get(slug=self.kwargs['slug'])

        # eventual filter on programma
        programma = None
        if self.inner_filter == 'programma':
            programma = ProgrammaAsseObiettivo.objects.get(pk=self.kwargs['codice'])

        # loop over all territories
        # foreach, invoke the tematizzazione method, with specified filters
        for t in self.queryset:
            data[t.codice] = getattr(Progetto.objects, tematizzazione)(
                    territorio=t,
                    tema=tema,
                    classificazione=natura,
                    programma=programma,
            )
            if data[t.codice]:
                nonzero_data[t.codice] = data[t.codice]

        # DataClassifier instance

        # computes number of bins
        n_bins = 4
        n_values = len(nonzero_data)
        if n_values < 4:
            n_bins = n_values
        self.dc = DataClassifier(nonzero_data.values(), classifier_args={'k': n_bins}, colors_map=self.colors)
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

    @cached_context
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TerritorioView, self).get_context_data(**kwargs)

        logger = logging.getLogger('console')
        logger.debug("get_aggregate_data start")
        context = self.get_aggregate_data(context, territorio=self.object)

        logger.debug("top_progetti_per_costo start")
        context['top_progetti_per_costo'] = Progetto.objects.nel_territorio(self.object).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]

        logger.debug("ultimi_progetti_conclusi start")
        context['ultimi_progetti_conclusi'] = Progetto.objects.conclusi().nel_territorio(self.object)[:5]

        logger.debug("territori_piu_finanziati_pro_capite start")
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
        except (Territorio.DoesNotExist, Territorio.MultipleObjectsReturned):
            pass

        return context


class ProvinciaView(TerritorioView):
    tipo_territorio = Territorio.TERRITORIO.P


class ComuneView(TerritorioView):
    tipo_territorio = Territorio.TERRITORIO.C


class AmbitoNazionaleView(TerritorioView):
    tipo_territorio = Territorio.TERRITORIO.N


class AmbitoEsteroView(AccessControlView, AggregatoView, ListView):
    queryset = Territorio.objects.filter(territorio=Territorio.TERRITORIO.E)

    @cached_context
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AmbitoEsteroView, self).get_context_data(**kwargs)

        logger = logging.getLogger('console')

        territori = self.queryset.all()

        logger.debug("totale_costi start")
        context['totale_costi'] = Progetto.objects.totale_costi(territori=territori)
        logger.debug("totale_pagamenti start")
        context['totale_pagamenti'] = Progetto.objects.totale_pagamenti(territori=territori)
        logger.debug("totale_progetti start")
        context['totale_progetti'] = Progetto.objects.totale_progetti(territori=territori)

        context['percentuale_costi_pagamenti'] = "{0:.0%}".format(
            context['totale_pagamenti'] /
            context['totale_costi'] if context['totale_costi'] > 0.0 else 0.0
        )
        # read tematizzazione GET param
        context['tematizzazione'] = self.request.GET.get('tematizzazione', 'totale_costi')

        query_models = {
            'temi_principali' : {
                'manager': Tema.objects,
                'parent_class_field': 'tema_superiore',
                'manager_parent_method': 'principali',
                'filter_name': 'tema',
                },
            'nature_principali' : {
                'manager': ClassificazioneAzione.objects,
                'parent_class_field': 'classificazione_superiore',
                'manager_parent_method': 'tematiche',
                'filter_name': 'classificazione'
            }
        }

        # specialize the filter
        query_filters = dict(territori=territori)


        for name in query_models:
            context[name] = []
            # takes all root models ( principali or tematiche )
            for object in getattr(query_models[name]['manager'], query_models[name]['manager_parent_method'])():
                q = query_filters.copy()
                # add %model%_superiore to query filters
                q[query_models[name]['filter_name']] = object
                # make query and add totale to object
                # object.tot = query_models[name]['manager'].filter( **q ).aggregate( tot=aggregate_field )['tot']
                logger.debug("totale_{0}, models: {1}, object: {2} -- start".format(
                    context['tematizzazione'],
                    query_models[name],
                    object
                ))

                object.tot = getattr(Progetto.objects, context['tematizzazione'])(**q)
                # add object to right context
                context[name].append( object )

        logger.debug('top_progetti_per_costo start')
        context['top_progetti_per_costo'] = Progetto.objects.nei_territori(territori).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico').distinct()[:5]
        logger.debug('last_progetti_conclusi start')
        context['ultimi_progetti_conclusi'] = Progetto.objects.conclusi().nei_territori( territori )[:5]

#        context['nazioni_piu_finanziate'] = self.queryset.annotate(totale=models.Sum('progetto__fin_totale_pubblico')).filter( totale__isnull=False ).order_by('-totale')

        progetti_multi_territorio = []
        multi_territori = {}
        # per ogni progetto multi-localizzato nel db
        logger.debug('blob multiloc start')

        for progetto in Progetto.objects.annotate(tot=Count('territorio_set')).filter(tot__gt=1).select_related('territori'):
            # se ha nei suoi territori un territorio estero..
            if any([x in territori for x in progetto.territori]):
                progetti_multi_territorio.append(progetto.pk)
                key = ", ".join(sorted([t.denominazione for t in progetto.territori]))
                if key not in multi_territori: multi_territori[key] = []
                multi_territori[key].append(progetto.pk)

        context['lista_finanziamenti_per_nazione'] = [
            (nazione, getattr(
                Progetto.objects.exclude(pk__in=progetti_multi_territorio).nel_territorio( nazione ),
                context['tematizzazione'])() )
            for nazione in territori
        ]

        for key in multi_territori:
            context['lista_finanziamenti_per_nazione'].append(
                (
                    Territorio(denominazione=key,territorio='E'), getattr(Progetto.objects.filter(pk__in=multi_territori[key]), context['tematizzazione'])()
                )
            )

        context['territori_esteri'] = territori

        return context


class RegioneCSVView(CSVView):
    model = Territorio

    def write_csv(self, response):
        territorio_filter = self.object.get_cod_dict()
        writer = utils.UnicodeWriter(response)
        writer.writerow( self.get_first_row() )
        comuni = list(Territorio.objects.comuni().filter(**territorio_filter).defer('geom'))
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