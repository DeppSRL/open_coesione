# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Sum
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
                    default='./popolazione.csv',
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

        self.logger.info("Reset dei dati a zero")
        Territorio.objects.update(
            popolazione_totale=0,
            popolazione_maschile=0,
            popolazione_femminile=0
        )

        self.logger.info("Inizio import da %s" % self.csv_file)


        self.logger.info("Aggiornamento comuni")
        for r in self.csv_reader:
            c = self.csv_reader.reader.line_num - 1

            # determina territorio a partire da codice comune e regione
            try:
                territorio = Territorio.objects.get(cod_reg=int(r['CODICE REGIONE'][0:2]), cod_com=int(r['CODICE COMUNE']))
            except ObjectDoesNotExist:
                self.logger.warning("{0} - Territorio non trovato: {1}-{2}, skipping".format(c, r['CODICE REGIONE'], r['CODICE COMUNE']))
                continue

            territorio.popolazione_totale += int(r['TOTALE'])
            territorio.popolazione_maschile += int(r['MASCHI'])
            territorio.popolazione_femminile += int(r['FEMMINE'])
            territorio.save()
            self.logger.info(
                u"{0} - {1.denominazione} - T:{1.popolazione_totale} M:{1.popolazione_maschile} F:{1.popolazione_femminile}".format(c, territorio)
            )


        self.logger.info("Aggiornamento province")
        for t in Territorio.objects.filter(territorio=Territorio.TERRITORIO.P):
            pop = Territorio.objects.filter(territorio='C', cod_prov=t.cod_prov).\
                aggregate(
                    tot=Sum('popolazione_totale'),
                    m=Sum('popolazione_maschile'),
                    f=Sum('popolazione_femminile')
                )
            t.popolazione_totale += int(pop['tot'])
            t.popolazione_maschile += int(pop['m'])
            t.popolazione_femminile += int(pop['f'])
            t.save()
            self.logger.info(
                u"{0.denominazione} - T:{0.popolazione_totale} M:{0.popolazione_maschile} F:{0.popolazione_femminile}".format(t)
            )

        self.logger.info("Aggiornamento regioni")
        for t in Territorio.objects.filter(territorio=Territorio.TERRITORIO.R):
            pop = Territorio.objects.filter(territorio='P', cod_reg=t.cod_reg).\
            aggregate(
                tot=Sum('popolazione_totale'),
                m=Sum('popolazione_maschile'),
                f=Sum('popolazione_femminile')
            )
            t.popolazione_totale += int(pop['tot'])
            t.popolazione_maschile += int(pop['m'])
            t.popolazione_femminile += int(pop['f'])
            t.save()
            self.logger.info(
                u"{0.denominazione} - T:{0.popolazione_totale} M:{0.popolazione_maschile} F:{0.popolazione_femminile}".format(t)
            )

        self.logger.info("Fine")




