# -*- coding: utf-8 -*-
import subprocess
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db.models import Count

from optparse import make_option
from soggetti.models import Soggetto

import logging

class Command(BaseCommand):
    """
    Generate cached content by visiting pages, uses request.

    """
    help = "Generate cached content for aggregate pages or recipients"

    option_list = BaseCommand.option_list + (
        make_option('--dryrun',
                    dest='dryrun',
                    action='store_true',
                    default=False,
                    help='Show generated urls'),
        make_option('--clear-cache',
                    action='store_true',
                    dest='clearcache',
                    default=False,
                    help='Clear the cache, before extracting the data'),
        make_option('--type',
                    dest='type',
                    default=None,
                    help='Type of generation: recipients,home, temi, nature, regioni, province, estero, programmi'),
        make_option('--big-recipients-treshold',
                    dest='big_recipients_treshold',
                    default='100',
                    help='Treshold for progetti.count to be considered a big recipient'),
    )

    logger = logging.getLogger('console')

    def handle(self, *args, **options):

        self.dryrun = options['dryrun']

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
        if cache_type is None:
            raise Exception("No --type option, choose among 'recipients, home', 'temi', 'nature', 'regioni', 'province', 'estero', 'programmi'")
        if cache_type not in ('recipients', 'home', 'temi', 'nature', 'regioni', 'province', 'estero', 'programmi'):
            raise Exception("Wrong --type option: choose among 'recipients', 'home', 'temi', 'nature', 'regioni', 'province', 'estero', 'programmi'")

        # invoke correct handler method,
        # passes along the correct view class, url_name and tipo_territorio, if needed
        handlers = {
            'recipients': self.handle_recipients,
            'home': self.handle_home,
            'temi': self.handle_temi,
            'nature': self.handle_nature,
            'regioni': self.handle_regioni,
            'province': self.handle_province,
            'estero': self.handle_estero,
            'programmi': self.handle_programmi,
        }
        handlers[cache_type](*args, **options)


    def handle_home(self, *args, **options):
        self.logger.info("== regenerating cache for home page")
        self._aggregate_cache_computation(
            '', page_type='home',
            clearcache=options['clearcache'], verbosity=options['verbosity']
        )

    def handle_temi(self, *args, **options):
        self.logger.info("== regenerating cache for temi")
        from progetti.models import Tema
        temi_slugs = (item['slug'] for item in Tema.objects.filter(tipo_tema=Tema.TIPO.sintetico).values('slug'))
        for tema_slug in temi_slugs:
            self._aggregate_cache_computation(
                tema_slug, page_type='tema',
                clearcache=options['clearcache'], verbosity=options['verbosity']
            )

    def handle_nature(self, *args, **options):
        self.logger.info("== regenerating cache for nature")
        from progetti.models import ClassificazioneAzione
        nature_slugs = (item['slug'] for item in ClassificazioneAzione.objects.filter(tipo_classificazione=ClassificazioneAzione.TIPO.natura).values('slug'))
        for natura_slug in nature_slugs:
            self._aggregate_cache_computation(
                natura_slug, page_type='natura',
                clearcache=options['clearcache'], verbosity=options['verbosity']
            )

    def handle_programmi(self, *args, **options):
        self.logger.info("== regenerating cache for programmi")
        from progetti.models import ProgrammaAsseObiettivo
        codes = (item['codice'] for item in ProgrammaAsseObiettivo.objects.programmi().values('codice'))
        for code in codes:
            self._aggregate_cache_computation(
                code, page_type='programma',
                clearcache=options['clearcache'], verbosity=options['verbosity']
            )

    def handle_estero(self, *args, **options):
        self.logger.info("== regenerating cache for ambito estero")
        self._aggregate_cache_computation(
            '', page_type='ambitoestero',
            clearcache=options['clearcache'], verbosity=options['verbosity']
        )


    def handle_regioni(self, *args, **options):
        self.logger.info("== regenerating cache for regioni")
        from territori.models import Territorio
        territori_slugs = (item['slug'] for item in Territorio.objects.filter(territorio=Territorio.TERRITORIO.R).values('slug'))
        for territorio_slug in territori_slugs:
            self.logger.debug("    :: regione {0}".format(territorio_slug))
            self._aggregate_cache_computation(
                territorio_slug, page_type='regione',
                clearcache=options['clearcache'], verbosity=options['verbosity'],
                tipo_territorio='regione'
            )


    def handle_province(self, *args, **options):
        self.logger.info("== regenerating cache for province")
        from territori.models import Territorio
        territori_slugs = (item['slug'] for item in Territorio.objects.filter(territorio=Territorio.TERRITORIO.P).values('slug'))
        for territorio_slug in territori_slugs:
            self._aggregate_cache_computation(
                territorio_slug, page_type='provincia',
                clearcache=options['clearcache'], verbosity=options['verbosity'],
                tipo_territorio='provincia'
            )



    def _aggregate_cache_computation(self, slug, page_type, clearcache, verbosity, tipo_territorio=None):
        if not self.dryrun:
            self.logger.info("== Executing prepareaggregate for {0}".format(slug))
            for thematization in ('', 'totale_costi', 'totale_costi_procapite', 'totale_pagamenti', 'totale_progetti'):
                call_command('prepareaggregate', slug,
                             type=page_type,
                             clearcache=clearcache,
                             verbosity=verbosity,
                             thematization=thematization,
                             tipo_territorio=tipo_territorio)
        else:
            self.logger.info("== Blocking execution for {0}, due to --dryrun option".format(slug))





    def handle_recipients(self, *args, **options):
        treshold = options['big_recipients_treshold']
        self.logger.info("== regenerating cache for recipients with more than {0} projects".format(treshold))
        grandi_soggetti = Soggetto.objects.all().annotate(n=Count('progetto')).filter(n__gt=treshold).order_by('n')
        self.logger.info("== building urls list")
        for s in grandi_soggetti:
            if self.dryrun:
                self.logger.info("{0}; n_progetti: {1}".format(s.slug, s.progetti.count()))
            else:
                self.logger.info("{0}; n_progetti: {1}".format(s.slug, s.progetti.count()))
                subprocess.call(
                    ["python",  "manage.py",  "preparesoggetto", s.slug,
                    "--clear-cache" if options['clearcache'] else "",
                    "--verbosity={0}".format(options['verbosity'])])


                for thematization in ('totale_costi', 'totale_pagamenti', 'totale_progetti'):
                    subprocess.call(
                        ["python",  "manage.py",  "preparesoggetto", s.slug,
                        "--clear-cache" if options['clearcache'] else "",
                        "--verbosity={0}".format(options['verbosity']),
                        "--thematization={0}".format(thematization)])









