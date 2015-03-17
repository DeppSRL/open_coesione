# -*- coding: utf-8 -*-
from optparse import make_option
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.test import RequestFactory
import logging

from open_coesione.views import HomeView
from progetti.views import ClassificazioneAzioneView, TemaView, ProgrammaView, ProgrammiView
from territori.models import Territorio
from territori.views import TerritorioView, MapnikRegioniView, MapnikProvinceView, MapnikComuniView, LeafletView, AmbitoNazionaleView, AmbitoEsteroView
from django.core.cache import cache

from open_coesione.utils import setup_view

class Command(BaseCommand):
    """
    Extracts all relevant information to build the specified aggregate page.
    Page type can be one of the following:

    * home
    * tipologia
    * tema
    * programma
    * territorio

    This mimics the process done during a standard http request,
    in order to debug and optimize it.
    """
    help = "Extracts relevant information to build the aggregate page"

    logger = logging.getLogger('console')
    thematization = ''
    slug = '' #it may refer to a code, for programmi pages
    page_type = ''
    clearcache = False

    option_list = BaseCommand.option_list + (
        make_option('--clear-cache',
                    action='store_true',
                    dest='clearcache',
                    default=False,
                    help='Clear the cache for the soggetto, before extracting the data'),
        make_option('--thematization',
                    dest='thematization',
                    default='',
                    help='One of totale_costi, totale_pagamenti, totale_progetti'),
        make_option('--type',
                    dest='type',
                    default='home',
                    help='One of home, tema, natura, programma, territorio'),
    )

    def handle(self, *args, **options):

        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)


        self.page_type = options['type']
        if (self.page_type != 'home' and
            self.page_type != 'ambitoestero' and
            self.page_type != 'ambitonazionale'):
            if args:
                if len(args) > 1:
                    raise Exception("Please insert just one slug")
                self.slug = args[0]
            else:
                raise Exception("Please insert at least a slug")

        if options['thematization']:
            self.thematization = "?tematizzazione={0}".format(options['thematization'])
        else:
            self.thematization = ""

        if options['thematization'] not in ('', 'totale_costi', 'totale_pagamenti', 'totale_progetti', 'totale_costi_procapite'):
            raise Exception(
                "Wrong thematization {0}. Choose one among 'totale_costi', 'totale_pagamenti', 'totale_progetti', 'totale_costi_procapite'".format(
                    options['thematization']
                ))

        self.clearcache = options['clearcache']


        # invoke correct handler method,
        # passes along the correct view class, url_name and tipo_territorio, if needed
        handlers = {
            'home': (self.handle_home, {
                'aggregate_view_class': HomeView,
                'url_name': 'home',
                'mapnik_url_names_views': (
                    { 'name': 'territori_mapnik_regioni',
                      'view': MapnikRegioniView },
                    { 'name': 'territori_mapnik_province',
                      'view': MapnikProvinceView },
                ),
                'leaflet_url_names': (
                    { 'name':  'territori_leaflet_regioni' },
                    { 'name':  'territori_leaflet_province' },
                ),
            }),
            'tema': (self.handle_other, {
                'aggregate_view_class': TemaView,
                'url_name': 'progetti_tema',
                'inner_filter': 'tema',
                'mapnik_url_names_views': (
                    { 'name': 'territori_mapnik_regioni_tema',
                      'view': MapnikRegioniView },
                    { 'name': 'territori_mapnik_province_tema',
                      'view': MapnikProvinceView },
                ),
                'leaflet_url_names': (
                    { 'name':  'territori_leaflet_regioni_tema' },
                    { 'name':  'territori_leaflet_province_tema' },
                ),
            }),
            'natura': (self.handle_other, {
                'aggregate_view_class': ClassificazioneAzioneView,
                'url_name': 'progetti_tipologia',
                'inner_filter': 'natura',
                'mapnik_url_names_views': (
                    { 'name': 'territori_mapnik_regioni_natura',
                      'view': MapnikRegioniView },
                    { 'name': 'territori_mapnik_province_natura',
                      'view': MapnikProvinceView },
                ),
                'leaflet_url_names': (
                    { 'name':  'territori_leaflet_regioni_natura' },
                    { 'name':  'territori_leaflet_province_natura' },
                ),
            }),
            'programma': (self.handle_other, {
                'aggregate_view_class': ProgrammaView,
                'url_name': 'progetti_programma',
                'inner_filter': 'programma',
                'mapnik_url_names_views': (
                    { 'name': 'territori_mapnik_regioni_programma',
                      'view': MapnikRegioniView },
                    { 'name': 'territori_mapnik_province_programma',
                      'view': MapnikProvinceView },
                ),
                'leaflet_url_names': (
                    { 'name': 'territori_leaflet_regioni_programma' },
                    { 'name': 'territori_leaflet_province_programma' },
                )
            }),
            'programmi': (self.handle_other, {
                'aggregate_view_class': ProgrammiView,
                'url_name': 'progetti_programmi',
                'inner_filter': 'gruppo_programmi',
                'mapnik_url_names_views': (
                    { 'name': 'territori_mapnik_regioni_gruppoprogrammi',
                      'view': MapnikRegioniView },
                    { 'name': 'territori_mapnik_province_gruppoprogrammi',
                      'view': MapnikProvinceView },
                ),
                'leaflet_url_names': (
                    { 'name': 'territori_leaflet_regioni_gruppoprogrammi' },
                    { 'name': 'territori_leaflet_province_gruppoprogrammi' },
                )
            }),
            'regione': (self.handle_other, {
                'aggregate_view_class': TerritorioView,
                'url_name': 'territori_regione',
                'tipo_territorio': Territorio.TERRITORIO.R,
                'mapnik_url_names_views': (
                    { 'name': 'territori_mapnik_province_regione',
                      'view': MapnikProvinceView },
                    { 'name': 'territori_mapnik_comuni_regione',
                      'view': MapnikComuniView },
                ),
                'leaflet_url_names': (
                    { 'name':  'territori_leaflet_province_regione' },
                    { 'name':  'territori_leaflet_comuni_regione' },
                ),
            }),
            'provincia': (self.handle_other, {
                'aggregate_view_class': TerritorioView,
                'url_name': 'territori_provincia',
                'tipo_territorio': Territorio.TERRITORIO.P,
                'mapnik_url_names_views': (
                    { 'name': 'territori_mapnik_comuni_provincia',
                      'view': MapnikComuniView },
                ),
                'leaflet_url_names': (
                    { 'name':  'territori_leaflet_comuni_provincia' },
                ),
            }),
            'ambitoestero': (self.handle_ambito_estero, {
                'aggregate_view_class': AmbitoEsteroView,
                'url_name': 'territori_estero',
            }),
            # 'ambitonazionale': (self.handle_ambito, {
            #     'aggregate_view_class': AmbitoNazionaleView,
            #     'url_name': 'territori_nazionale',
            # }),

        }
        try:
            handlers[self.page_type][0](**handlers[self.page_type][1])
        except Exception as e:
            self.logger.error(
                "{0} catched. type: {1}, slug: {2}, thematization: {3}".format(
                    e, self.page_type, self.slug, self.thematization
                )
            )


    def handle_home(self, *args, **kwargs):
        self.logger.info("Home page, Thematization: {0}".format(self.thematization))
        mapnik_url_names_views = kwargs['mapnik_url_names_views']
        leaflet_url_names = kwargs['leaflet_url_names']

        if self.clearcache:
            cache_key = "context/{0}".format(self.thematization)
            self.logger.info("Clearing the cache for key {0}".format(cache_key))
            cache.delete(cache_key)

            for nv in mapnik_url_names_views:
                mapnik_url = reverse(nv['name'])
                cache_key = "context{0}{1}".format(mapnik_url, self.thematization)
                self.logger.info("Clearing the cache for key {0}".format(cache_key))
                cache.delete(cache_key)

            for n in leaflet_url_names:
                leaflet_url = reverse(n['name'], kwargs={'ext': 'json'})
                cache_key = "context{0}{1}".format(leaflet_url, self.thematization)
                self.logger.info("Clearing the cache for key {0}".format(cache_key))
                cache.delete(cache_key)


        aggregate_view_class = kwargs['aggregate_view_class']
        view = setup_view(
            aggregate_view_class(),
            RequestFactory().get("/{0}".format(self.thematization)),
        )
        context = view.get_context_data()
        self.logger.info("context for /{0} fetched::::".format(self.thematization))

        for nv in mapnik_url_names_views:
            mapnik_url = reverse(nv['name'])
            mapnik_view = nv['view']
            view = setup_view(
                mapnik_view(),
                RequestFactory().get("{0}{1}".format(mapnik_url, self.thematization)),
            )
            context = view.get_context_data()
            self.logger.info("context for {0}{1} fetched::::".format(mapnik_url, self.thematization))

        for n in leaflet_url_names:
            leaflet_url = reverse(n['name'], kwargs={'ext': 'json'})
            leaflet_view = LeafletView
            view = setup_view(
                leaflet_view(),
                RequestFactory().get("{0}{1}".format(leaflet_url, self.thematization)),
            )
            context = view.get_context_data()
            self.logger.info("context for {0}{1} fetched::::".format(leaflet_url, self.thematization))

    def handle_ambito_estero(self, *args, **kwargs):
        self.logger.info("{0} page, Thematization: {1}".format(self.page_type, self.thematization))

        url_name = kwargs['url_name']
        url = reverse(url_name)
        req = RequestFactory().get("{0}{1}".format(url, self.thematization))

        if self.clearcache:
            cache_key = "context{0}{1}".format(url, self.thematization)
            self.logger.info("Clearing the cache for key {0}".format(cache_key))
            cache.delete(cache_key)


        aggregate_view_class = kwargs['aggregate_view_class']
        view = setup_view(
            aggregate_view_class(),
            req,
        )

        context = view.get_context_data(object_list=Territorio.objects.filter(territorio=Territorio.TERRITORIO.E))
        self.logger.info("context for {0}{1} fetched::::".format(url, self.thematization))

    def handle_other(self, *args, **kwargs):
        self.logger.info("{0} page, Slug: {1}, Thematization: {2}".format(self.page_type, self.slug, self.thematization))
        mapnik_url_names_views = kwargs['mapnik_url_names_views']
        leaflet_url_names = kwargs['leaflet_url_names']
        inner_filter = kwargs.pop('inner_filter', None)

        if 'tipo_territorio' in kwargs:
            t = Territorio.objects.get(slug=self.slug)

        # get the URL from the url_name, using the slug
        url_name = kwargs['url_name']
        if 'programma' in url_name:
            url = reverse(url_name, kwargs={'codice': self.slug})
        else:
            url = reverse(url_name, kwargs={'slug': self.slug})

        # build mapnik urls, and views arrays
        # considering territorio special case
        mapnik_urls = []
        mapnik_views = []
        for nv in mapnik_url_names_views:
            mapnik_views.append(nv['view'])
            if 'tipo_territorio' in kwargs:
                if kwargs['tipo_territorio'] == Territorio.TERRITORIO.R:
                    mapnik_urls.append(reverse(nv['name'], kwargs={'cod_reg': t.cod_reg}))
                if kwargs['tipo_territorio'] == Territorio.TERRITORIO.P:
                    mapnik_urls.append(reverse(nv['name'], kwargs={'cod_prov': t.cod_prov}))
            else:
                if 'programma' in url_name:
                    mapnik_urls.append(reverse(nv['name'], kwargs={'codice': self.slug}))
                else:
                    mapnik_urls.append(reverse(nv['name'], kwargs={'slug': self.slug}))

        leaflet_urls = []
        for n in leaflet_url_names:
            if 'tipo_territorio' in kwargs:
                if kwargs['tipo_territorio'] == Territorio.TERRITORIO.R:
                    leaflet_urls.append(reverse(n['name'], kwargs={'ext': 'json', 'cod_reg': t.cod_reg}))
                if kwargs['tipo_territorio'] == Territorio.TERRITORIO.P:
                    leaflet_urls.append(reverse(n['name'], kwargs={'ext': 'json', 'cod_prov': t.cod_prov}))
            else:
                if 'programma' in url_name:
                    leaflet_urls.append(reverse(n['name'], kwargs={'ext': 'json', 'codice': self.slug}))
                else:
                    leaflet_urls.append(reverse(n['name'], kwargs={'ext': 'json', 'slug': self.slug}))

        # check the cache, and remove the keys, if asked
        if self.clearcache:
            cache_key = "context{0}{1}".format(url, self.thematization)
            self.logger.info("Clearing the cache for key {0}".format(cache_key))
            cache.delete(cache_key)

            for mapnik_url in mapnik_urls:
                cache_key = "context{0}{1}".format(mapnik_url, self.thematization)
                self.logger.info("Clearing the cache for key {0}".format(cache_key))
                cache.delete(cache_key)
            for leaflet_url in leaflet_urls:
                cache_key = "context{0}{1}".format(leaflet_url, self.thematization)
                self.logger.info("Clearing the cache for key {0}".format(cache_key))
                cache.delete(cache_key)

        aggregate_view_class = kwargs['aggregate_view_class']

        # prepare the view
        view_instance = aggregate_view_class()
        req = RequestFactory().get("{0}{1}".format(url, self.thematization))
        if 'programma' in url_name:
            view = setup_view(
                view_instance,
                req,
                codice=self.slug, inner_filter=inner_filter
            )
        else:
            view = setup_view(
                view_instance,
                req,
                slug=self.slug, inner_filter=inner_filter
            )

        # add tipo_territorio to view, in case it's passed
        # since, it's needed to extract the Territorio instance
        # from the slug
        if 'tipo_territorio' in kwargs:
            self.logger.debug("Tipo territorio: {0}".format(kwargs['tipo_territorio']))
            view.tipo_territorio = kwargs['tipo_territorio']

        # get the object instance using the view's get_object method
        view.object = view.get_object()

        # emulate the get_context_data method call
        context = view.get_context_data()
        self.logger.info("context for {0}{1} fetched::::".format(url, self.thematization))

        # repeat for mapnik urls
        for (k, mapnik_url) in enumerate(mapnik_urls):
            mapnik_req = RequestFactory().get("{0}{1}".format(mapnik_url, self.thematization))
            mapnik_view = mapnik_views[k]
            if 'tipo_territorio' in kwargs:
                if kwargs['tipo_territorio'] == Territorio.TERRITORIO.R:
                    view = setup_view(
                        mapnik_view(),
                        mapnik_req,
                        cod_reg=t.cod_reg,
                    )
                if kwargs['tipo_territorio'] == Territorio.TERRITORIO.P:
                    view = setup_view(
                        mapnik_view(),
                        mapnik_req,
                        cod_prov=t.cod_prov,
                    )
            else:
                if 'programma' in url_name:
                    view = setup_view(
                        mapnik_view(),
                        mapnik_req,
                        codice=self.slug, inner_filter=inner_filter
                    )
                else:
                    view = setup_view(
                        mapnik_view(),
                        mapnik_req,
                        slug=self.slug, inner_filter=inner_filter
                    )

            self.logger.debug("fetching context for {0}{1}::::".format(mapnik_url, self.thematization))
            self.logger.debug("|-context args: {0}::::".format(view.args))
            self.logger.debug("|-context kwargs: {0}::::".format(view.kwargs))
            context = view.get_context_data(*view.args, **view.kwargs)
            self.logger.info("context for {0}{1} fetched::::".format(mapnik_url, self.thematization))


        # repeat for leaflet urls
        for leaflet_url in leaflet_urls:
            leaflet_req = RequestFactory().get("{0}{1}".format(leaflet_url, self.thematization))
            leaflet_view = LeafletView
            if 'tipo_territorio' in kwargs:
                if kwargs['tipo_territorio'] == Territorio.TERRITORIO.R:
                    view = setup_view(
                        leaflet_view(),
                        leaflet_req,
                        cod_reg=t.cod_reg,
                        ext='json',
                    )
                if kwargs['tipo_territorio'] == Territorio.TERRITORIO.P:
                    view = setup_view(
                        leaflet_view(),
                        leaflet_req,
                        cod_prov=t.cod_prov,
                        ext='json'
                    )
            else:
                if 'programma' in url_name:
                    view = setup_view(
                        leaflet_view(),
                        leaflet_req,
                        codice=self.slug, inner_filter=inner_filter,
                        ext='json'
                    )
                else:
                    view = setup_view(
                        leaflet_view(),
                        leaflet_req,
                        slug=self.slug, inner_filter=inner_filter,
                        ext='json'
                    )

            self.logger.debug("fetching context for {0}{1}::::".format(leaflet_url, self.thematization))
            context = view.get_context_data(*view.args, **view.kwargs)
            self.logger.info("context for {0}{1} fetched::::".format(leaflet_url, self.thematization))
