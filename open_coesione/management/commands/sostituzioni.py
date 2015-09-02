# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from optparse import make_option
import csvkit
from progetti.models import *


class Command(BaseCommand):
    """
    CIPE assignments that enters DPS monitoring as full-fledged projects, are marked as non-active overlapping projects
    """
    help = 'Read the CSV mapping of overlapping CIPE assignments and mark them as non active'

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

    logger = logging.getLogger('csvimport')

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

        dryrun = options['dryrun']

        csv_file = options['csvfile']

        # read csv file
        try:
            unicode_reader = csvkit.unicsv.UnicodeCSVDictReader(open(csv_file, 'r'), delimiter=';', encoding='utf-8-sig')
        except IOError:
            self.logger.error(u'It was impossible to open file {}'.format(csv_file))
        except Exception as e:
            self.logger.error(u'CSV error while reading {}: {}'.format(csv_file, e.message))
        else:
            self.logger.info(u'Inizio import da {}'.format(csv_file))
            self.logger.info(u'Limit: {}'.format(options['limit']))
            self.logger.info(u'Offset: {}'.format(options['offset']))

            for r in unicode_reader:
                c = unicode_reader.reader.line_num - 1

                if c < int(options['offset']):
                    continue

                if int(options['limit']) and (c - int(options['offset']) > int(options['limit'])):
                    break

                # codice locale progetto (ID del record)
                try:
                    p = Progetto.fullobjects.get(pk=r['COD_LOCALE_PROGETTO'])
                except ObjectDoesNotExist:
                    self.logger.warning(u'{} - Progetto non trovato: {}, skipping'.format(c, r['COD_LOCALE_PROGETTO']))
                    continue

                try:
                    p_cipe = Progetto.fullobjects.get(pk=r['COD_DIPE'])
                except ObjectDoesNotExist:
                    self.logger.warning(u'{} - Assegnazione CIPE non trovata: {}, skipping'.format(c, r['COD_DIPE']))
                    continue

                self.logger.info(u'{}, Assegnazione: {}, Progetto: {}'.format(c, p_cipe, p))
                if not dryrun:
                    p.overlapping_projects.add(p_cipe)
                    p_cipe.active_flag = False
                    p_cipe.save()

            self.logger.info(u'Fine')
