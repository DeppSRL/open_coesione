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
    help = "Import data from csv"

    option_list = BaseCommand.option_list + (
        make_option('--treshold',
                    dest='treshold',
                    default='100',
                    help='Ectract only soggetti with a number of progetti greather than this'),
    )

    def handle(self, *args, **options):
        self.treshold = options['treshold']

        grandi_soggetti = Soggetto.objects.all().annotate(n=Count('progetto')).filter(n__gt=self.treshold).order_by('-n')
        for s in grandi_soggetti:
            print "%s;%s" % (s.get_absolute_url(), s.n)








