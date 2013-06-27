# -*- coding: utf-8 -*-
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

        view = setup_view(
            SoggettoView(),
            RequestFactory().get('/soggetti/{0}'.format(slug)),
            soggetto
        )


        #pr = cProfile.Profile()
        #pr.enable()
        context = view.get_context_data()
        #pr.disable()
        #ps = pstats.Stats(pr)
        #ps.sort_stats('cumulative')
        #ps.print_stats(.1)



def setup_view(view, request, soggetto, *args, **kwargs):
    """Mimic as_view() returned callable, but returns view instance.

    args and kwargs are the same you would pass to ``reverse()``

    """
    view.request = request
    view.object = soggetto
    view.args = args
    view.kwargs = kwargs
    return view