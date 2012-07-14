# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option
import csv
import logging
from open_coesione import utils
from progetti.models import *


class Command(BaseCommand):
    """
    Progetti titles' corrections are read and updated
    """
    help = "Import data from csv"

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csvfile',
                    default='./progetti.csv',
                    help='Select csv file'),
        make_option('--limit',
                    dest='limit',
                    default=0,
                    help='Limit of records to import'),
        make_option('--offset',
                    dest='offset',
                    default=0,
                    help='Offset of records to import'),
        make_option('--dry-run',
                    dest='dryrun',
                    action='store_true',
                    default=False,
                    help='Set the dry-run command mode: no actual modification is made'),
        make_option('--encoding',
                    dest='encoding',
                    default='iso-8859-1',
                    help='set character encoding of input file')
        )

    csv_file = ''
    encoding = 'iso-8859-1'
    logger = logging.getLogger('csvimport')
    unicode_reader = None

    def handle(self, *args, **options):
        self.csv_file = options['csvfile']

        # read first csv file
        try:
            self.unicode_reader = utils.UnicodeDictReader(open(self.csv_file, 'rb'), delimiter=';', encoding=self.encoding)
        except IOError:
            self.logger.error("It was impossible to open file %s" % self.csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s" % (self.csv_file, e.message))

        self.encoding = options['encoding']

        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        dryrun = options['dryrun']

        self.logger.info("Inizio import da %s" % self.csv_file)
        self.logger.info("Encoding: %s" % self.encoding)
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        n = 0
        for r in self.unicode_reader:
            c = self.unicode_reader.reader.line_num - 1
            if c < int(options['offset']):
                continue

            if int(options['limit']) and\
               (c - int(options['offset']) > int(options['limit'])):
                break

            # codice locale progetto (ID del record)
            try:
                progetto = Progetto.objects.get(pk=r['COD_LOCALE_PROGETTO'])
                titolo = r['DPS_TITOLO_PROGETTO']
                if progetto.titolo_progetto is None or progetto.titolo_progetto != titolo:
                    progetto.titolo = titolo
                    n += 1
                    if not dryrun:
                        progetto.save()
                    self.logger.info("%s, %s - Progetto: %s aggiornato" % (n, c, progetto.codice_locale))
                else:
                    self.logger.debug("%s, %s - Progetto: %s NON aggiornato" % (n, c, progetto.codice_locale))
            except ObjectDoesNotExist:
                self.logger.debug("%s - Progetto non trovato: %s, skipping" % (c, r['COD_LOCALE_PROGETTO']))
                continue



        self.logger.info("Fine")






