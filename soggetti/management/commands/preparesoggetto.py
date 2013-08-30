# -*- coding: utf-8 -*-
from optparse import make_option
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.test import RequestFactory
import logging

from soggetti.models import Soggetto
from soggetti.views import SoggettoView
from open_coesione.utils import setup_view

class Command(BaseCommand):
    """
    Extracts all relevant information to build the soggetto page.
    This mimics the process done during a standard http request,
    in order to debug and optimize it.
    """
    help = "Extracts relevant information to build the soggetto page"

    logger = logging.getLogger('console')

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

        if args:
            if len(args) > 1:
                raise Exception("Please insert one slug")
            slug = args[0]

            if options['thematization']:
                thematization = "?tematizzazione={0}".format(options['thematization'])
            else:
                thematization = ""

            if options['thematization'] not in ('', 'totale_costi', 'totale_pagamenti', 'totale_progetti'):
                raise Exception("Wrong thematization. Choose one among 'totale_costi', 'totale_pagamenti', 'totale_progetti'")

            try:
                soggetto = Soggetto.objects.get(slug=slug)
            except ObjectDoesNotExist:
                raise Exception("Unknown soggetto {0}".format(slug))
        else:
            raise Exception("Please insert a slug for a soggetto")

        self.logger.info(u"Soggetto: {0}, Tematizzazione: {1}".format(soggetto.denominazione, thematization))

        # get the URL from the url_name, using the slug
        url = reverse('soggetti_soggetto', kwargs={'slug': slug})

        if options['clearcache']:
            cache_key = "context{0}{1}".format(url, thematization)
            self.logger.info(u"Clearing the cache for key {0}{1}".format(cache_key, thematization))
            from django.core.cache import cache
            cache.delete(cache_key)

        view = setup_view(
            SoggettoView(),
            RequestFactory().get("{0}{1}".format(url, thematization)),
            slug=slug,
        )
        view.object = view.get_object()

        context = view.get_context_data(*view.args, **view.kwargs)
        self.logger.info("Context fetched::::")
