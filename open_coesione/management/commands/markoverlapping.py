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
    CIPE assignments that enters DPS monitoring as full-fledged projects,
    are marked as non-active overlapping projects
    """
    help = "Read the CSV mapping of overlapping CIPE assignments and mark them as non active"

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csvfile',
                    default='dati/dataset_latest/sostituzioni.csv',
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
        )

    csv_file = ''
    logger = logging.getLogger('csvimport')
    unicode_reader = None

    def handle(self, *args, **options):
        self.csv_file = options['csvfile']

        # read first csv file
        try:
            self.unicode_reader = utils.UnicodeDictReader(open(self.csv_file, 'r'), delimiter=';', encoding='utf8')
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

        dryrun = options['dryrun']

        self.logger.info("Inizio import da %s" % self.csv_file)
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
                p = Progetto.objects.get(pk=r['COD_LOCALE_PROGETTO'])
            except ObjectDoesNotExist:
                self.logger.warning("%s - Progetto non trovato: %s, skipping" % (c, r['COD_LOCALE_PROGETTO']))
                continue

            try:
                p_cipe = Progetto.objects.get(pk=r['COD_DIPE'])
            except ObjectDoesNotExist:
                self.logger.warning("%s - Assegnazione CIPE non trovata: %s, skipping" % (c, r['COD_DIPE']))
                continue

            self.logger.info(u"%s, Assegnazione: %s, Progetto: %s" % (c, p_cipe, p))
            if not dryrun:
                p.overlapping_projects.add(p_cipe)
                p_cipe.active_flag = False
                p_cipe.save()


        self.logger.info("Fine")






