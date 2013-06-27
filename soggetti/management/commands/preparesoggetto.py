# -*- coding: utf-8 -*-
from optparse import make_option
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from django.test import RequestFactory
import logging

from soggetti.models import Soggetto
from soggetti.views import SoggettoView

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

        print("Verbosity: {0}".format(verbosity))

        if args:
            if len(args) > 1:
                raise Exception("Please insert one slug")
            slug = args[0]
            try:
                soggetto = Soggetto.objects.get(slug=slug)
            except ObjectDoesNotExist:
                raise Exception("Unknown soggetto {0}".format(slug))
        else:
            raise Exception("Please insert a slug for a soggetto")

        self.logger.info("Soggetto: {0}".format(soggetto.denominazione))

        soggetto_path = '/soggetti/{0}/'.format(slug)
        if options['clearcache']:
            cache_key = "context/soggetti/{0}/".format(slug)
            self.logger.info("Clearing the cache for key {0}".format(cache_key))
            from django.core.cache import cache
            cache.delete(cache_key)

        view = setup_view(
            SoggettoView(),
            RequestFactory().get("/soggetti/{0}/".format(slug)),
            soggetto
        )

        context = view.get_context_data()
        self.logger.info("Context fetched::::")



def setup_view(view, request, soggetto, *args, **kwargs):
    """Mimic as_view() returned callable, but returns view instance.

    args and kwargs are the same you would pass to ``reverse()``

    """
    view.request = request
    view.object = soggetto
    view.args = args
    view.kwargs = kwargs
    return view
