# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from optparse import make_option
import csvkit
from progetti.models import *


class Command(BaseCommand):
    """
    Projects belonging to many programs, get multiple fonti
    """
    help = 'Read the CSV mapping of overlappings fonti, and assign them to the projects'

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csvfile',
                    default='dati/dataset_latest/sovrapposizioni.csv',
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
        csv_file = options['csvfile']

        # read csv file
        try:
            unicode_reader = csvkit.unicsv.UnicodeCSVDictReader(open(csv_file, 'r'), delimiter=';', encoding='utf-8-sig')
        except IOError:
            self.logger.error(u'It was impossible to open file {}'.format(csv_file))
            exit(1)
        except Exception as e:
            self.logger.error(u'CSV error while reading {}: {}'.format(csv_file, e.message))
            exit(1)

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

        fonti = {f.codice: f for f in Fonte.objects.all()}

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
                self.logger.info(u'{} - Progetto: {}'.format(c, r['COD_LOCALE_PROGETTO']))
            except ObjectDoesNotExist:
                self.logger.warning(u'{} - Progetto non trovato: {}, skipping'.format(c, r['COD_LOCALE_PROGETTO']))
                continue

            # remove old fonti
            codici_precedenti = p.fonte_set.values_list('codice', flat=True)
            for codice in codici_precedenti:
                p.fonte_set.remove(fonti[codice])
            self.logger.debug(u'  Rimossi codici precedenti: {}'.format(','.join(codici_precedenti)))

            # add new fonti
            codici_attuali = [k for k in r.keys() if r[k] == u'1']
            for codice in codici_attuali:
                p.fonte_set.add(fonti[codice])
            self.logger.debug(u'  Aggiunti codici attuali: {}'.format(','.join(codici_attuali)))

        self.logger.info(u'Fine')
