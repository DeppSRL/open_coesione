# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from cache_generation.visitor import Visitor

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
                    help='Type of generation: aggregate|recipients'),
        make_option('--type',
                    dest='type',
                    default=None,
                    help='Type of generation: aggregate|recipients'),
        make_option('--host',
                    dest='host',
                    default='http://localhost:8020',
                    help='Host prefix, http://DOMAIN, no slash at the end'),
        make_option('--big-recipients-treshold',
                    dest='big_recipients_treshold',
                    default='100',
                    help='Treshold for progetti.count to be considered a big recipient'),
    )

    logger = logging.getLogger('cachegenerator')
    host = ''
    suffixes = [
     "",
     "?tematizzazione=totale_costi",
     "?tematizzazione=totale_pagamenti",
     "?tematizzazione=totale_progetti",
    ]
    map_suffixes = suffixes + ["?tematizzazione=totale_costi_procapite",]

    def handle(self, *args, **options):

        self.host = options['host']
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

        if options['type'] == 'aggregate':
            self.handle_aggregate(*args, **options)
        elif options['type'] == 'recipients':
            self.handle_recipients(*args, **options)
        else:
            self.logger.error("Wrong type %s. Select among 'aggregate' and 'recipients'." % options['type'])
            exit(1)


    def handle_aggregate(self, *args, **options):
        v = Visitor()
        v.set_logger(self.logger)

        self.logger.info("== regenerating cache for aggregate pages")

        self.logger.info("== regenerating cache for home page")
        url = "{0}/".format(self.host)
        self.logger.debug("{0}".format(url))
        self.add_urls_to_visitor(page = "", visitor=v)

        self.logger.info("== regenerating cache for temi")
        from progetti.models import Tema
        temi = Tema.objects.filter(tipo_tema=Tema.TIPO.sintetico)
        for t in temi:
            url = "{0}/progetti/temi/{1}".format(self.host, t.slug)
            self.logger.debug("{0}".format(url))
            self.add_urls_to_visitor(page = "/temi/{0}".format(t.slug), visitor=v, prefix="progetti")


        self.logger.info("== regenerating cache for nature")
        from progetti.models import ClassificazioneAzione
        nature = ClassificazioneAzione.objects.filter(tipo_classificazione=ClassificazioneAzione.TIPO.natura)
        for n in nature:
            url = "{0}/progetti/tipologie/{1}".format(self.host, n.slug)
            self.logger.debug("{0}".format(url))
            self.add_urls_to_visitor(page = "/tipologie/{0}".format(n.slug), visitor=v, prefix="progetti")


        self.logger.info("== regenerating cache for regioni")
        from territori.models import Territorio
        territori = Territorio.objects.filter(territorio=Territorio.TERRITORIO.R)
        for t in territori:
            url = "{0}/territori/regioni/{1}".format(self.host, t.slug)
            self.logger.debug("{0}".format(url))
            self.add_urls_to_visitor(page = "/regioni/{0}".format(t.slug), visitor=v, prefix="territori")

        self.logger.info("== regenerating cache for province")
        from territori.models import Territorio
        territori = Territorio.objects.filter(territorio=Territorio.TERRITORIO.P)
        for t in territori:
            url = "{0}/territori/province/{1}".format(self.host, t.slug)
            self.logger.debug("{0}".format(url))
            self.add_urls_to_visitor(page = "/province/{0}".format(t.slug), visitor=v, prefix="province")

        if self.dryrun:
            v.display()
        else:
            self.logger.info("== visiting urls")
            v.visit()



    def add_urls_to_visitor(self, page, visitor, prefix=""):
        """
        adds all urls to the visitor object,
        needed to correctly cache a page in all of its status and all related maps
        """
        for suffix in self.map_suffixes:
            for location_type in ('regioni', 'province'):
                visitor.add_url("{host}/territori/mapnik{page}/{location_type}.xml{suffix}".format(
                    host=self.host,
                    page=page,
                    location_type=location_type,
                    suffix=suffix))
                visitor.add_url("{host}/territori/leaflet{page}/{location_type}.json{suffix}".format(
                    host=self.host,
                    page=page,
                    location_type=location_type,
                    suffix=suffix))
        for suffix in self.suffixes:
            visitor.add_url("{host}/{prefix}{page}{suffix}".format(
                host=self.host,
                page=page,
                prefix=prefix,
                suffix=suffix))


    def handle_recipients(self, *args, **options):
        treshold = options['big_recipients_treshold']

        v = Visitor()
        v.set_logger(self.logger)

        self.logger.info("== regenerating cache for recipients with more than {0} projects".format(treshold))

        grandi_soggetti = Soggetto.objects.all().annotate(n=Count('progetto')).filter(n__gt=treshold).order_by('n')
        self.logger.info("== building urls list")
        for s in grandi_soggetti:
            url = "{0}{1}".format(self.host, s.get_absolute_url())
            self.logger.debug("{0};{1}".format(url, s.n))
            for suffix in self.suffixes:
                v.add_url("{0}{1}".format(url, suffix))


        if self.dryrun:
            v.display()
        else:
            self.logger.info("== visiting urls")
            v.visit()








