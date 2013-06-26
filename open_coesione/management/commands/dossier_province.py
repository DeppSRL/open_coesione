# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import connection
from django.db.utils import DatabaseError
from django.core.management.base import BaseCommand
import sys

from open_coesione import utils
from optparse import make_option
from decimal import Decimal
import csv
import logging
import datetime

from progetti.models import Progetto
from territori.models import Territorio

class Command(BaseCommand):
    """
    Which provinces get the money, subduvuded by regions?
    """
    help = "Which provinces get the money, subduvuded by regions?"

    option_list = BaseCommand.option_list + (
        make_option('--region',
                    dest='region',
                    help='Region name, or nothing to get all provinces'),
    )

    logger = logging.getLogger('csvimport')
    unicode_writer = None

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

        csv_writer = utils.UnicodeWriter(sys.stdout, dialect=utils.excel_semicolon)
        csv_writer.writerow(self.get_first_row())

        ## fetch provinces
        if options['region']:
            try:
                reg = Territorio.objects.get(territorio='R', denominazione__icontains=options['region'])
                provs = Territorio.objects.filter(cod_reg=reg.cod_reg, territorio='P')
            except ObjectDoesNotExist:
                raise Exception("Unknown region {0}".format(options['region']))
            costo = Progetto.objects.totale_costi(territorio=reg)
            costo_procapite = Progetto.objects.totale_costi_procapite(territorio=reg)
        else:
            provs = Territorio.objects.filter(territorio='P')
            costo = Progetto.objects.totale_costi()
            costo_procapite = Progetto.objects.totale_costi_procapite()

        for prov in provs:
            costo_prov = Progetto.objects.totale_costi(territorio=prov)
            costo_procapite_prov = Progetto.objects.totale_costi_procapite(territorio=prov)
            csv_writer.writerow([
                prov.denominazione,
                "{0:.2f}".format(costo_prov),
                "{0:.2f}".format(costo_procapite_prov),
                "{0:.2f}".format(costo_prov/costo*100),
            ])

        csv_writer.writerow([
            "TOTALE",
            "{0:.2f}".format(costo),
            "{0:.2f}".format(costo_procapite),
            "{0:.2f}".format(100),
        ])

    def get_first_row(self):
        return ['Provincia', 'Finanziamento totale', 'Finanziamento pro capite', 'Percentuale finanziamento regionale']





