# -*- coding: utf-8 -*-
from optparse import make_option
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from django.test import RequestFactory
import logging

from open_coesione.views import HomeView
from progetti.views import TipologiaView, TemaView
from territori.views import TerritorioView

from open_coesione.utils import setup_view

class Command(BaseCommand):
    """
    Extracts all relevant information to build the specified aggregate page.
    Page type can be one of the following:

    * home
    * tipologia
    * tema
    * territorio

    This mimics the process done during a standard http request,
    in order to debug and optimize it.
    """
    help = "Extracts relevant information to build the aggregate page"

    logger = logging.getLogger('console')
    thematization = ''
    slug = ''
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
                    help='One of home, tema, tipologia, territorio'),
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
        if self.page_type != 'home':
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

        if options['thematization'] not in ('', 'totale_costi', 'totale_pagamenti', 'totale_progetti'):
            raise Exception("Wrong thematization. Choose one among 'totale_costi', 'totale_pagamenti', 'totale_progetti'")

        self.clearcache = options['clearcache']

        # invoke correct handler method,
        # passes the correct view, along
        handlers = {
            'home': self.handle_home,
            'tema': self.handle_other,
            'tipologia': self.handle_other,
            'territorio': self.handle_other,
        }
        handlers[self.page_type]()


    def handle_home(self):
        self.logger.info("Home page, Thematization: {0}".format(self.thematization))

        # home_path = '/{0}'.format(thematization)
        if self.clearcache:
            cache_key = "context//{0}".format(self.thematization)
            self.logger.info("Clearing the cache for key {0}".format(cache_key))
            from django.core.cache import cache
            cache.delete(cache_key)

        view = setup_view(
            HomeView(),
            RequestFactory().get("/{0}".format(self.thematization)),
            None
        )
        context = view.get_context_data()
        self.logger.info("Context fetched::::")

    def handle_other(self):
        self.logger.info("{0} page, Slug: {1}, Thematization: {2}".format(self.page_type, self.slug, self.thematization))
        if self.clearcache:
            cache_key = "context/{0}/{1}".format(self.slug, self.thematization)
            self.logger.info("Clearing the cache for key {0}".format(cache_key))
            from django.core.cache import cache
            cache.delete(cache_key)

        aggregate_view = ???
        aggregate_model = ???

        try:
            obj_instance = aggregate_model.objects.get(slug=self.slug)
        except ObjectDoesNotExist:
            raise Exception("Unknown {0} {0}".format(self.page_type, self.slug))

        view = setup_view(
            aggregate_view(),
            RequestFactory().get("/{0}/{1}".format(self.slug, self.thematization)),
            obj_instance
        )
        context = view.get_context_data()
        self.logger.info("Context fetched::::")
