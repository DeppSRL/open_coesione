# -*- coding: utf-8 -*-
import logging
from django.core.management.base import BaseCommand

from optparse import make_option
from django.core.urlresolvers import reverse, resolve
from django.test import RequestFactory

import datetime

from progetti.search_querysets import sqs


class Command(BaseCommand):
    """
    """
    help = ''

    option_list = BaseCommand.option_list + (
        make_option('--encoding',
                    dest='encoding',
                    default='utf-8-sig',
                    help='Set character encoding of input file.'),
    )

    logger = logging.getLogger(__name__)

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

        start_time = datetime.datetime.now()

        request = RequestFactory().get('{}{}'.format(reverse('progetti_search_csv'), '?q='))

        view_class = resolve(request.path).func.__class__
        view = view_class(searchqueryset=sqs)
        response = view(request)

        # print(response.content)

        duration = datetime.datetime.now() - start_time
        seconds = round(duration.total_seconds())

        self.logger.info(u'Fine. Tempo di esecuzione: {:02d}:{:02d}:{:02d}.'.format(int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)))
