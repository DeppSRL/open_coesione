# -*- coding: utf-8 -*-
import logging
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.test import RequestFactory
from open_coesione.utils import setup_view
from open_coesione.views import HomeView
from optparse import make_option
from progetti.views import ClassificazioneAzioneView, TemaView, ProgrammaView, ProgrammiView
from soggetti.views import SoggettoView
from territori.models import Territorio
from territori.views import MapnikRegioniView, MapnikProvinceView, MapnikComuniView, AmbitoEsteroView, RegioneView, ProvinciaView


class Command(BaseCommand):
    """
    Extracts all relevant information to build the specified aggregate page.
    This mimics the process done during a standard http request, in order to debug and optimize it.
    """

    help = 'Extracts relevant information to build the aggregate page'

    page_types = {
        'home': {
            'aggregate_view_class': HomeView,
            'url_name': 'home',
            'mapnik_url_names_views': (
                {'name': 'territori_mapnik_regioni', 'view': MapnikRegioniView},
                {'name': 'territori_mapnik_province', 'view': MapnikProvinceView},
            ),
        },
        'tema': {
            'aggregate_view_class': TemaView,
            'url_name': 'progetti_tema',
            'inner_filter': 'tema',
            'mapnik_url_names_views': (
                {'name': 'territori_mapnik_regioni_tema', 'view': MapnikRegioniView},
                {'name': 'territori_mapnik_province_tema', 'view': MapnikProvinceView},
            ),
        },
        'natura': {
            'aggregate_view_class': ClassificazioneAzioneView,
            'url_name': 'progetti_tipologia',
            'inner_filter': 'natura',
            'mapnik_url_names_views': (
                {'name': 'territori_mapnik_regioni_natura', 'view': MapnikRegioniView},
                {'name': 'territori_mapnik_province_natura', 'view': MapnikProvinceView},
            ),
        },
        'programma': {
            'aggregate_view_class': ProgrammaView,
            'url_name': 'progetti_programma',
            'inner_filter': 'programma',
            'mapnik_url_names_views': (
                {'name': 'territori_mapnik_regioni_programma', 'view': MapnikRegioniView},
                {'name': 'territori_mapnik_province_programma', 'view': MapnikProvinceView},
            ),
        },
        'programmi': {
            'aggregate_view_class': ProgrammiView,
            'url_name': 'progetti_programmi',
            'inner_filter': 'gruppo_programmi',
            'mapnik_url_names_views': (
                {'name': 'territori_mapnik_regioni_gruppoprogrammi', 'view': MapnikRegioniView},
                {'name': 'territori_mapnik_province_gruppoprogrammi', 'view': MapnikProvinceView},
            ),
        },
        'regione': {
            'aggregate_view_class': RegioneView,
            'url_name': 'territori_regione',
            'mapnik_url_names_views': (
                {'name': 'territori_mapnik_province_regione', 'view': MapnikProvinceView},
                {'name': 'territori_mapnik_comuni_regione', 'view': MapnikComuniView},
            ),
        },
        'provincia': {
            'aggregate_view_class': ProvinciaView,
            'url_name': 'territori_provincia',
            'mapnik_url_names_views': (
                {'name': 'territori_mapnik_comuni_provincia', 'view': MapnikComuniView},
            ),
        },
        'ambitoestero': {
            'aggregate_view_class': AmbitoEsteroView,
            'url_name': 'territori_estero',
        },
        'soggetto': {
            'aggregate_view_class': SoggettoView,
            'url_name': 'soggetti_soggetto',
        },
    }

    option_list = BaseCommand.option_list + (
        make_option('--type',
                    dest='type',
                    default=None,
                    help='Page type; choose among {}.'.format(', '.join('"{}"'.format(t) for t in page_types))),
        make_option('--slug',
                    dest='slug',
                    default=None,
                    help='Page object slug'),
        make_option('--clear-cache',
                    action='store_true',
                    dest='clearcache',
                    default=False,
                    help='Clear the cache for the view, before extracting the data'),
    )

    logger = logging.getLogger('console')

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

        page_type = options['type']

        if page_type in ('home', 'ambitoestero'):
            slug = ''
        else:
            slug = options['slug']
            if not slug:
                self.logger.error('Please insert a slug')
                exit(1)

        try:
            self._handle(page_type, slug, options['clearcache'], self.page_types[page_type])
        except Exception as e:
            self.logger.error('{} catched. type: {}, slug: {}'.format(e, page_type, slug))

    def _handle(self, page_type, slug, clearcache, params):
        self.logger.info('{} page, slug: {}'.format(page_type, slug))

        mapnik_url_names_views = params.get('mapnik_url_names_views', ())
        inner_filter = params.get('inner_filter')

        aggregate_view_class = params['aggregate_view_class']

        url_name = params['url_name']
        if slug:
            slug_cond = {'codice' if 'programma' in url_name else 'slug': slug}
        else:
            slug_cond = {}
        url = reverse(url_name, kwargs=slug_cond)

        if page_type in ('regione', 'provincia'):
            mapnik_cond = Territorio.objects.get(slug=slug).get_cod_dict()
        else:
            mapnik_cond = slug_cond

        # build mapnik urls and views list considering territorio special case
        mapnik_urls_views = [{'url': reverse(x['name'], kwargs=mapnik_cond), 'view': x['view']} for x in mapnik_url_names_views]

        # check the cache, and remove the keys, if asked
        if clearcache:
            self._clearcache([url] + [x['url'] for x in mapnik_urls_views])

        view = setup_view(aggregate_view_class(), RequestFactory().get(url), inner_filter=inner_filter, **slug_cond)

        # # add tipo_territorio to view in case it's passed, since it's needed to extract the Territorio instance from the slug
        # if 'tipo_territorio' in params:
        #     view.tipo_territorio = params['tipo_territorio']

        # get the object instance using the view's get_object method
        if hasattr(view, 'get_object'):
            view.object = view.get_object()

        # emulate the get_context_data method call
        if page_type == 'ambitoestero':
            view.get_context_data(object_list=Territorio.objects.filter(territorio=Territorio.TERRITORIO.E), *view.args, **view.kwargs)
        else:
            view.get_context_data(*view.args, **view.kwargs)
        self.logger.info('context for {} fetched::::'.format(url))

        for mapnik_url_view in mapnik_urls_views:
            view = setup_view(mapnik_url_view['view'](), RequestFactory().get(mapnik_url_view['url']), inner_filter=inner_filter, **mapnik_cond)
            view.get_context_data(*view.args, **view.kwargs)
            self.logger.info('context for {} fetched::::'.format(mapnik_url_view['url']))

    def _clearcache(self, urls):
        from django.core.cache import cache

        for url in urls:
            cache_key = 'context{}'.format(url)
            self.logger.info('Clearing the cache for key {}'.format(cache_key))
            cache.delete(cache_key)
