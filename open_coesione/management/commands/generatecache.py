# -*- coding: utf-8 -*-
import datetime
import logging
# import subprocess
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.models import Count
from optparse import make_option


class Command(BaseCommand):
    """
    Generate cached content by visiting pages, uses request.
    """

    help = 'Generate cached content for aggregate pages or soggetti'

    cache_types = ['home', 'temi', 'nature', 'regioni', 'provincie', 'estero', 'programmi', 'gruppiprogrammi', 'soggetti']

    option_list = BaseCommand.option_list + (
        make_option('--type',
                    dest='type',
                    default=None,
                    help='Type of cache; choose among {}.'.format(', '.join('"{}"'.format(t) for t in cache_types))),
        make_option('--clear-cache',
                    dest='clearcache',
                    action='store_true',
                    default=False,
                    help='Clear the cache, before extracting the data.'),
        make_option('--dryrun',
                    dest='dryrun',
                    action='store_true',
                    default=False,
                    help='Show generated urls.'),
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

        cache_type = options['type']

        if cache_type not in self.cache_types:
            self.logger.error(u'Wrong --type option "{}". Choose among {}.'.format(cache_type, ', '.join('"{}"'.format(t) for t in self.cache_types)))
        else:
            self.logger.info(u'Regenerating cache for "{}".'.format(cache_type))

            start_time = datetime.datetime.now()

            method = getattr(self, 'handle_{}'.format(cache_type))
            method(**options)

            duration = datetime.datetime.now() - start_time
            seconds = round(duration.total_seconds())

            self.logger.info(u'Done. Execution time: {:02d}:{:02d}:{:02d}.'.format(int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)))

    def handle_home(self, **options):
        self._aggregate_cache_computation('', page_type='home', **options)

    def handle_temi(self, **options):
        from progetti.models import Tema

        for slug in Tema.objects.principali().values_list('slug', flat=True):
            self._aggregate_cache_computation(slug, page_type='tema', **options)

    def handle_nature(self, **options):
        from progetti.models import ClassificazioneAzione

        for slug in ClassificazioneAzione.objects.nature().values_list('slug', flat=True):
            self._aggregate_cache_computation(slug, page_type='natura', **options)

    def handle_regioni(self, **options):
        from territori.models import Territorio

        for slug in Territorio.objects.regioni().values_list('slug', flat=True):
            self._aggregate_cache_computation(slug, page_type='regione', **options)

    def handle_provincie(self, **options):
        from territori.models import Territorio

        for slug in Territorio.objects.provincie().values_list('slug', flat=True):
            self._aggregate_cache_computation(slug, page_type='provincia', **options)

    def handle_estero(self, **options):
        self._aggregate_cache_computation('', page_type='ambitoestero', **options)

    def handle_programmi(self, **options):
        from progetti.models import Progetto, ProgrammaAsseObiettivo, ProgrammaLineaAzione

        prog_classifications = [
            {'class': ProgrammaAsseObiettivo, 'attribute': 'programma_asse_obiettivo'},
            {'class': ProgrammaLineaAzione, 'attribute': 'programma_linea_azione'}
        ]
        for prog_classification in prog_classifications:
            filter_key = '{}__classificazione_superiore__classificazione_superiore'.format(prog_classification['attribute'])
            for code in prog_classification['class'].objects.programmi().values_list('codice', flat=True):
                n_progetti = Progetto.objects.filter(**{filter_key: code}).count()
                if n_progetti >= settings.BIG_PROGRAMMI_THRESHOLD:
                    self.logger.info('Program {}. Generating cache for {} projects.'.format(code, n_progetti))
                    self._aggregate_cache_computation(code, page_type='programma', **options)
                else:
                    self.logger.info('Program {}. Skipping cache generation for {} projects.'.format(code, n_progetti))

    def handle_gruppiprogrammi(self, **options):
        from progetti.gruppo_programmi import GruppoProgrammi

        for slug in GruppoProgrammi.GRUPPI_PROGRAMMI.keys():
            self._aggregate_cache_computation(slug, page_type='programmi', **options)

    def handle_soggetti(self, **options):
        from soggetti.models import Soggetto

        self.logger.info('== building urls list')
        for soggetto in Soggetto.objects.annotate(n=Count('progetto')).filter(n__gt=settings.BIG_SOGGETTI_THRESHOLD).order_by('n'):
            self.logger.info('Soggetto {}. Generating cache for {} projects.'.format(soggetto.slug, soggetto.n))
            self._aggregate_cache_computation(soggetto.slug, page_type='soggetto', **options)
            # if not options['dryrun']:
            #     subprocess.call(['python', 'manage.py', 'preparesoggetto', soggetto.slug, '--clear-cache' if options['clearcache'] else '', '--verbosity={}'.format(options['verbosity'])])

    def _aggregate_cache_computation(self, slug, page_type, **options):
        if not options['dryrun']:
            self.logger.info('== Executing prepareaggregate for "{}"'.format(slug))
            call_command('prepareaggregate', slug=slug, type=page_type, clearcache=options['clearcache'], verbosity=options['verbosity'])
        else:
            self.logger.info('== Blocking execution for "{}", due to --dryrun option'.format(slug))
