# -*- coding: utf-8 -*-
import json
import re
import urllib
from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db.models import Count
from django.http import HttpResponse, Http404
from django.template.defaultfilters import slugify
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from models import Territorio
from open_coesione.data_classification import DataClassifier
from open_coesione.views import AggregatoMixin, cached_context
from progetti.gruppo_programmi import GruppoProgrammi
from progetti.models import Progetto, Tema, ClassificazioneAzione, ProgrammaAsseObiettivo, ProgrammaLineaAzione
from progetti.views import BaseCSVView


class JSONResponseMixin(object):
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/json'
        serializable_context = context.copy()
        serializable_context.pop('view', None)
        return self.response_class(
            json.dumps(serializable_context),
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
            territori = [(t.denominazione, t.get_progetti_search_url(tema=tema)) for t in territorio_hierarchy]

        natura = None
        if self.filter == 'nature':
            natura = ClassificazioneAzione.objects.get(slug=kwargs['slug'])
            territori = [(t.denominazione, t.get_progetti_search_url(natura=natura)) for t in territorio_hierarchy]

        programma = None
        gruppo_programmi = None
        programmi = None
        if self.filter == 'programmi':
            try:
                programma = ProgrammaLineaAzione.objects.get(codice=kwargs['slug'])
            except ProgrammaAsseObiettivo.DoesNotExist:
                programma = ProgrammaAsseObiettivo.objects.get(codice=kwargs['slug'])

            programmi = [programma]

            territori = [(t.denominazione, t.get_progetti_search_url(programma=programma)) for t in territorio_hierarchy]
        elif self.filter == 'gruppo_programmi':
            try:
                gruppo_programmi = GruppoProgrammi(codice=self.kwargs.get('slug'))
            except:
                raise Http404

            programmi = gruppo_programmi.programmi

            territori = [(t.denominazione, t.get_progetti_search_url(gruppo_programmi=gruppo_programmi)) for t in territorio_hierarchy]

        # prepare the cache key
        tema_key = tema.slug if tema is not None else 'na'
        natura_key = natura.slug if natura is not None else 'na'
        programmi_key = programma.codice if programma is not None else (gruppo_programmi.codice if gruppo_programmi is not None else 'na')
        cache_key = 'terr:{}_tema:{}_natura:{}_programmi:{}'.format(territorio.pk, tema_key, natura_key, programmi_key)

        # check vars existance in the cache, or compute and store them
        cached_vars = cache.get(cache_key)
        if cached_vars is None:
            progetti = Progetto.objects.nei_territori([territorio])
            if tema:
                progetti = progetti.con_tema(tema)
            if natura:
                progetti = progetti.con_natura(natura)
            if programmi:
                progetti = progetti.con_programmi(programmi)
            totali = progetti.totali()
            cached_vars = {
                'popolazione_totale': (territorio.popolazione_totale if territorio else Territorio.objects.nazione().popolazione_totale) or 0,
                'costo_totale': totali['totale_costi'],
                'n_progetti': totali['totale_progetti'],
                'pagamento_totale': totali['totale_pagamenti'],
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
        if query.startswith('='):
            territori = Territorio.objects.filter(slug=query[1:])
        else:
            territori = Territorio.objects.filter(denominazione__istartswith=query).order_by('-popolazione_totale')[0:20]
        context['territori'] = [{
            'denominazione': territorio.nome_con_provincia,
            'url': territorio.get_absolute_url(),
            'id': territorio.pk,
            'cod_com': territorio.cod_com,
            'cod_prov': territorio.cod_prov,
            'cod_reg': territorio.cod_reg,
            'slug': territorio.slug,
        } for territorio in territori]

        return context


class LeafletView(JSONResponseMixin, TemplateView):
    inner_filter = None
    layer = None

    @cached_context
    def get_cached_context_data(self, **kwargs):
        context = {}

        # fetch Geometry object to look at
        # - nation
        # - region
        # - province

        if 'cod_reg' in kwargs:
            area = Territorio.objects.regioni().get(cod_reg=kwargs['cod_reg']).geom
            context['zoom'] = {'min': 7, 'max': 10}
        elif 'cod_prov' in kwargs:
            area = Territorio.objects.provincie().get(cod_prov=kwargs['cod_prov']).geom
            context['zoom'] = {'min': 8, 'max': 11}
        else:  # Collect all comuni except 'Lampedusa e Linosa' to reduce zoomlevel of fitbound
            area = Territorio.objects.comuni().exclude(cod_com='84020').collect()
            context['zoom'] = {'min': 5, 'max': 7}

        # compute bounds, to use inside the maps
        context['bounds'] = {
            'southwest': {
                'lng': str(area.extent[0]),
                'lat': str(area.extent[1])
            },
            'northeast': {
                'lng': str(area.extent[2]),
                'lat': str(area.extent[3])
            }
        }

        if self.layer == 'world':
            context['zoom'] = {'min': 4, 'max': 11}
            context['layer_name'] = 'world'
            return context

        # compute layer name from request.path and tematizzazione query string

        tematizzazione = self.request.GET.get('tematizzazione', settings.MAP_TEMATIZZAZIONI[0])
        if tematizzazione not in settings.MAP_TEMATIZZAZIONI:
            raise Http404

        path = self.request.path.split('.')[0]
        context['layer_name'] = '_'.join(path.split('/')[3:]) + '_' + tematizzazione

        # layer type may be R, P or C
        context['layer_type'] = path.split('/')[-1:][0][0:1].upper()

        # read legend html directly from mapnik xml (which should be cached at this point)
        mapnik_host = settings.MAPNIK_HOST or Site.objects.get_current()
        mapnik_xml_path = '{}.xml?tematizzazione={}'.format(re.sub(r'leaflet', 'mapnik', path), tematizzazione)
        mapnik_xml_url = 'http://{}{}'.format(mapnik_host, mapnik_xml_path)
        try:
            mapnik_xml = urllib.urlopen(mapnik_xml_url)
        except IOError:
            raise Http404('Cannot retrieve mapnik xml ({})'.format(mapnik_xml_url))
        else:
            from lxml import etree
            context['legend_html'] = etree.parse(mapnik_xml, parser=etree.XMLParser()).getroot()[0].text

        # info_base_url for popup changes in case temi, nature, programmi or gruppiprogrammi filters are applied
        if self.inner_filter:
            try:
                pk = self.kwargs['slug']
            except:
                try:
                    pk = self.kwargs['codice']
                except:
                    raise Exception('Slug or codice must be in kwargs')

            # convert inner_filter to its plural when creating info url
            filter_plural = {
                'tema': 'temi',
                'natura': 'nature',
                'programma': 'programmi',
                'gruppo_programmi': 'gruppo-programmi',
            }[self.inner_filter]

            context['info_base_url'] = '/territori/info/{}/{}'.format(filter_plural, pk)
        else:
            context['info_base_url'] = '/territori/info'

        return context

    def get_context_data(self, **kwargs):
        context = super(LeafletView, self).get_context_data(**kwargs)

        context.update(self.get_cached_context_data(**kwargs))

        context['tilestache_url'] = settings.TILESTACHE_URL

        return context


class TilesConfigView(TemplateView):
    template_name = 'territori/tiles.cfg'
    content_type = 'application/json'

    def get_context_data(self, **kwargs):
        context = super(TilesConfigView, self).get_context_data(**kwargs)
        context['tematizzazioni'] = settings.MAP_TEMATIZZAZIONI
        context['regioni'] = Territorio.objects.regioni()
        context['province'] = Territorio.objects.provincie()
        context['temi'] = Tema.objects.principali()
        context['nature'] = ClassificazioneAzione.objects.nature()
        context['programmi'] = list(ProgrammaAsseObiettivo.objects.programmi()) + list(ProgrammaLineaAzione.objects.programmi())
        context['gruppi_programmi_codici'] = GruppoProgrammi.GRUPPI_PROGRAMMI.keys()
        context['mapnik_base_url'] = 'http://{}/territori/mapnik'.format(settings.MAPNIK_HOST or Site.objects.get_current())
        context['path_to_cache'] = settings.TILESTACHE_CACHE_PATH

        return context


class BaseMapnikView(AggregatoMixin, TemplateView):
    TEMATIZZAZIONI = settings.MAP_TEMATIZZAZIONI

    template_name = 'territori/mapnik.xml'
    content_type = 'application/xml'

    inner_filter = None
    queryset = None
    territori_name = None
    codice_field = None
    cod_fld = None
    srs = None
    shp_file = None

    @cached_context
    def get_cached_context_data(self):
        context = {}

        context['territori_name'] = self.territori_name
        context['codice_field'] = self.codice_field
        context['srs'] = self.srs
        context['shp_file'] = self.shp_file
        context['countries_shp_file'] = '{}/dati/countries/82945364-10m-admin-0-countries.shp'.format(settings.REPO_ROOT)

        progetti = Progetto.objects
        territori = self.queryset.defer('geom')

        # eventual filter on tema
        if self.inner_filter == 'tema':
            progetti = progetti.con_tema(Tema.objects.get(slug=self.kwargs['slug']))

        # eventual filter on natura
        if self.inner_filter == 'natura':
            progetti = progetti.con_natura(ClassificazioneAzione.objects.get(slug=self.kwargs['slug']))

        # eventual filter on programma or gruppo_programmi
        if self.inner_filter == 'programma':
            try:
                programma = ProgrammaLineaAzione.objects.get(pk=self.kwargs['codice'])
            except ProgrammaLineaAzione.DoesNotExist:
                try:
                    programma = ProgrammaAsseObiettivo.objects.get(pk=self.kwargs['codice'])
                except ProgrammaAsseObiettivo.DoesNotExist:
                    raise Exception('Could not find appropriate programma')
            progetti = progetti.con_programmi([programma])
        elif self.inner_filter == 'gruppo_programmi':
            try:
                gruppo_programmi = GruppoProgrammi(codice=self.kwargs['slug'])
            except:
                raise Exception('Could not find appropriate gruppo programmi')
            else:
                progetti = progetti.con_programmi(gruppo_programmi.programmi)

        context['territori'] = self.add_totali(territori, progetti.nei_territori(territori).totali_group_by('territorio_set__{}'.format(self.cod_fld)), self.cod_fld)

        return context

    def get_context_data(self, **kwargs):
        context = super(BaseMapnikView, self).get_context_data(**kwargs)

        self.refine_context(context)

        context.update(self.get_cached_context_data())

        tematizzazione = self.get_tematizzazione()

        for obj in context['territori']:
            obj.totale = obj.totali.get(tematizzazione.replace('_procapite', ''), 0)
            if tematizzazione.endswith('_procapite'):
                obj.totale = round(obj.totale / obj.popolazione_totale) if obj.popolazione_totale else 0

        context['data'] = {t.slug: t.totale for t in context['territori']}

        # DataClassifier instance

        colors_map = settings.MAP_COLORS

        n_bins = len(colors_map.keys()) - 1

        dc = DataClassifier([t.totale for t in context['territori'] if t.totale], classifier_args={'k': n_bins})

        context['classification_bins'] = dc.get_bins_ranges() if dc.dc else None

        context['territori'] = [{'codice': str(t.codice), 'colore': colors_map[dc.get_class(t.totale)]} for t in context['territori']]

        return context

    def refine_context(self, context):
        pass


class MapnikRegioniView(BaseMapnikView):
    queryset = Territorio.objects.regioni()
    territori_name = 'regioni'
    codice_field = 'COD_REG'
    cod_fld = 'cod_reg'
    srs = '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over'
    shp_file = '{}/dati/reg2011_g/regioni_stats.shp'.format(settings.REPO_ROOT)


class MapnikProvinceView(BaseMapnikView):
    queryset = Territorio.objects.provincie()
    territori_name = 'province'
    codice_field = 'COD_PRO'
    cod_fld = 'cod_prov'
    srs = '+proj=utm +zone=32 +ellps=intl +units=m +no_defs'
    shp_file = '{}/dati/prov2011_g/prov2011_g.shp'.format(settings.REPO_ROOT)

    def refine_context(self, context):
        if 'cod_reg' in context:
            cod_reg = context['cod_reg']
            self.queryset = self.queryset.filter(cod_reg=cod_reg)
            # self.territori_name = 'regioni_{}_province'.format(cod_reg)


class MapnikComuniView(BaseMapnikView):
    queryset = Territorio.objects.comuni()
    territori_name = 'comuni'
    codice_field = 'PRO_COM'
    cod_fld = 'cod_com'
    srs = '+proj=utm +zone=32 +ellps=intl +units=m +no_defs'
    shp_file = '{}/dati/com2011_g/com2011_g.shp'.format(settings.REPO_ROOT)

    def refine_context(self, context):
        if 'cod_reg' in context:
            cod_reg = context['cod_reg']
            self.queryset = self.queryset.filter(cod_reg=cod_reg)
            # self.territori_name = 'regioni_{}_comuni'.format(cod_reg)
        elif 'cod_prov' in context:
            cod_prov = context['cod_prov']
            self.queryset = self.queryset.filter(cod_prov=cod_prov)
            # self.territori_name = 'province_{}_comuni'.format(cod_prov)
        else:
            raise Exception('A region or a province must be specified for this view')


class BaseTerritorioView(AggregatoMixin, DetailView):
    model = Territorio
    tipo_territorio = None

    def get_object(self, queryset=None):
        try:
            if 'slug' in self.kwargs:
                return Territorio.objects.get(slug=slugify(self.kwargs['slug']), territorio=self.tipo_territorio)
            else:
                return Territorio.objects.get(territorio=self.tipo_territorio)
        except Territorio.DoesNotExist:
            raise Http404

    def get_progetti_queryset(self):
        return Progetto.objects.nei_territori([self.object])

    @cached_context
    def get_cached_context_data(self):
        context = self.get_aggregate_data()

        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(filters=self.object.get_cod_dict())

        return context

    def get_context_data(self, **kwargs):
        context = super(BaseTerritorioView, self).get_context_data(**kwargs)

        context.update(self.get_cached_context_data())

        self.tematizza_context_data(context)

        context['ultimi_progetti_conclusi'] = self.get_progetti_queryset().no_privacy().conclusi()[:5]

        return context


class RegioneView(BaseTerritorioView):
    tipo_territorio = Territorio.TERRITORIO.R

    def get_context_data(self, **kwargs):
        context = super(RegioneView, self).get_context_data(**kwargs)

        try:
            context['popolazione_nazionale'] = Territorio.objects.nazione().popolazione_totale
        except (Territorio.DoesNotExist, Territorio.MultipleObjectsReturned):
            pass

        return context


class ProvinciaView(BaseTerritorioView):
    tipo_territorio = Territorio.TERRITORIO.P


class ComuneView(BaseTerritorioView):
    tipo_territorio = Territorio.TERRITORIO.C


class AmbitoNazionaleView(BaseTerritorioView):
    tipo_territorio = Territorio.TERRITORIO.N


class AmbitoEsteroView(AggregatoMixin, ListView):
    tipo_territorio = Territorio.TERRITORIO.E
    queryset = Territorio.objects.filter(territorio=tipo_territorio)

    def get_progetti_queryset(self):
        return Progetto.objects.nei_territori(self.get_queryset())

    @cached_context
    def get_cached_context_data(self):
        context = self.get_aggregate_data()

        # add object_list to context, to make the get_context_data work in the setup_view environment
        # used in cache generators scripts and in the API
        # context['object_list'] = self.object_list if hasattr(self, 'object_list') else None

        progetti = self.get_progetti_queryset()

        territori = self.get_queryset()

        multi_territori = {}
        for progetto in progetti.annotate(cnt=Count('territorio_set')).filter(cnt__gt=1):
            key = ', '.join(sorted([t.denominazione for t in progetto.territori if t in territori]))
            multi_territori.setdefault(key, []).append(progetto.pk)

        # from itertools import chain
        # progetti_multilocalizzati_pks = list(chain.from_iterable(multi_territori.values()))
        progetti_multilocalizzati_pks = [item for sublist in multi_territori.values() for item in sublist]

        context['territori'] = self.add_totali(territori, progetti.exclude(pk__in=progetti_multilocalizzati_pks).totali_group_by('localizzazione__territorio_id'))

        for name, pks in multi_territori.items():
            territorio = Territorio(denominazione=name, territorio=Territorio.TERRITORIO.E)
            territorio.totali = Progetto.objects.filter(pk__in=pks).totali()
            context['territori'].append(territorio)

        context['territori'] = [t for t in context['territori'] if t.totali != {}]

        return context

    def get_context_data(self, **kwargs):
        context = super(AmbitoEsteroView, self).get_context_data(**kwargs)

        context.update(self.get_cached_context_data())

        self.tematizza_context_data(context)

        context['ultimi_progetti_conclusi'] = self.get_progetti_queryset().no_privacy().conclusi()[:5]

        return context


class TerritorioCSVView(BaseCSVView):
    model = Territorio

    def comuni_filter(self):
        return self.object.get_cod_dict()

    def comuni_con_pro_capite_filter(self):
        return self.object.get_cod_dict()
