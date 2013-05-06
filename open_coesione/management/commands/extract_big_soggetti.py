# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from optparse import make_option
from soggetti.models import Soggetto


class Command(BaseCommand):
    """
    Extracts and print soggetti over the specified treshold
    """
    help = "Extract soggetti with more than treshold progetti"

    option_list = BaseCommand.option_list + (
        make_option('--treshold',
                    dest='treshold',
                    default='100',
                    help='Ectract only soggetti with a number of progetti greather than this'),
        make_option('--curl',
                    dest='curl',
                    action='store_true',
                    default=False,
                    help='Output in a curl ready format'),
    )

    def handle(self, *args, **options):
        self.treshold = options['treshold']
        self.curl = options['curl']

        grandi_soggetti = Soggetto.objects.all().annotate(n=Count('progetto')).filter(n__gt=self.treshold).order_by('n')
        for s in grandi_soggetti:
            if self.curl:
                print "curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' ",\
                      "\"http://opencoesione.gov.it/%s{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti}\"\n >> cache_soggetti_generation.log" % s.get_absolute_url()
            else:
                print "%s;%s" % (s.get_absolute_url(), s.n)








