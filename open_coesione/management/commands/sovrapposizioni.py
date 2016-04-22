# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from optparse import make_option
import csvkit
from progetti.models import Progetto, Fonte


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

        csv_file = options['csvfile']

        try:
            unicode_reader = csvkit.unicsv.UnicodeCSVDictReader(open(csv_file, 'r'), delimiter=';', encoding='utf-8-sig')
        except IOError:
            self.logger.error(u'It was impossible to open file {}'.format(csv_file))
        except Exception as e:
            self.logger.error(u'CSV error while reading {}: {}'.format(csv_file, e.message))
        else:
            self.logger.info(u'Inizio import da {}'.format(csv_file))

            fonti = {f.codice: f for f in Fonte.objects.all()}

            for r in unicode_reader:
                c = unicode_reader.reader.line_num - 1

                try:
                    p = Progetto.fullobjects.get(codice_locale=r['COD_LOCALE_PROGETTO'])
                    self.logger.info(u'{} - Progetto: {}'.format(c, p))
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
