# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import DatabaseError
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from os import path
from optparse import make_option
import csv
import logging
import datetime

from territori.models import Territorio

class Command(BaseCommand):
    """
    Import population data for territorii
    """
    help = "Import population data from csv"

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csvfile',
                    default='./progetti.csv',
                    help='Select csv file'),
        )

    csv_file = ''
    logger = logging.getLogger('csvimport')

    def handle(self, *args, **options):
        self.csv_file = options['csvfile']

        # read first csv file
        try:
            self.csv_reader = csv.DictReader(open(self.csv_file, 'rb'), delimiter=',')
        except IOError:
            self.logger.error("It was impossible to open file %s" % self.csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s" % (self.csv_file, e.message))

        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        self.logger.info("Inizio import da %s" % self.csv_file)


        for r in self.csv_reader:
            c = self.csv_reader.reader.line_num - 1

            # determina territorio a partire da codice comune e regione
            try:
                territorio = Territorio.objects.get(cod_reg=int(r['CODICE REGIONE']), cod_com=int(r['CODICE COMUNE']))
                self.logger.debug(
                    "{0} - Territorio: {1.denominazione} ({1.cod_reg}-{1.cod_com})".format(c, territorio)
                )
            except ObjectDoesNotExist:
                self.logger.warning("{0} - Territorio non trovato: {1}-{2}, skipping".format(c, r['CODICE REGIONE'], r['CODICE COMUNE']))
                continue

            territorio.popolazione_totale = int(r['TOT'])
            territorio.popolazione_maschile = int(r['MASCHI'])
            territorio.popolazione_femminile = int(r['FEMMINILE'])
            territorio.save()
            self.logger.debug(
                "popolazione: {0.popolazione_totale} M:{0.popolazione_maschile} F:{0.popolazione_femminile}".format(territorio)
            )

        self.logger.info(u"Comuni aggiornati")



        self.logger.info("Fine")




