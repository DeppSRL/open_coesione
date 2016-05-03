# -*- coding: utf-8 -*-
import datetime
import logging
import pandas as pd
import urllib2
from cStringIO import StringIO
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from django.db import transaction
from optparse import make_option
from progetti.models import Progetto


class Command(BaseCommand):
    """
    Data are imported from their CSV sources.
    """
    help = 'Import data from csv'

    import_types = {
        'descrizioni-ponrec': {
            'import_method': '_update_descrizioni_ponrec',
        },
        'descrizioni-pongat': {
            'import_method': '_update_descrizioni_pongat',
        },
    }

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csv_file',
                    default=None,
                    help='Select csv files file.'),
        make_option('--import-type',
                    dest='import_type',
                    default=None,
                    help='Type of import; select among {}.'.format(', '.join(['"' + t + '"' for t in import_types]))),
        make_option('--encoding',
                    dest='encoding',
                    default='utf-8-sig',
                    help='Set character encoding of input file.'),
        make_option('--separator',
                    dest='separator',
                    default=';',
                    help='Set separator of input file.'),
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

        csvfile = options['csv_file']
        importtype = options['import_type']
        encoding = options['encoding']
        separator = options['separator']

        if not importtype in self.import_types:
            self.logger.error(u'Wrong type "{}". Select among {}.'.format(importtype, ', '.join(['"' + t + '"' for t in self.import_types])))
            exit(1)

        # read csv file
        try:
            self.logger.info(u'Reading file {} ....'.format(csvfile))

            csv = urllib2.urlopen(csvfile).read()
        except IOError:
            self.logger.error(u'It was impossible to open file {}'.format(csvfile))
        else:
            df = pd.read_csv(
                StringIO(csv.decode(encoding).encode('utf-8')),
                sep=separator,
                header=0,
                low_memory=True,
                dtype=object,
                encoding='utf-8',
                keep_default_na=False,
            )

            self.logger.info(u'Done.')

            df.fillna('', inplace=True)
            df.drop_duplicates(inplace=True)

            self.logger.info(u'Inizio import "{}" ({}).'.format(importtype, csvfile))

            start_time = datetime.datetime.now()

            method = getattr(self, str(self.import_types[importtype]['import_method']))
            method(df)

            duration = datetime.datetime.now() - start_time
            seconds = round(duration.total_seconds())

            self.logger.info(u'Fine. Tempo di esecuzione: {:02d}:{:02d}:{:02d}.'.format(int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)))

    @transaction.commit_on_success
    def _update_descrizioni_ponrec(self, df):
        df = df[df['Sintesi'].str.strip() != '']

        df_count = len(df)

        report = {'updated': 0, 'not_found': 0}

        for n, (index, row) in enumerate(df.iterrows(), 1):
            codice = '1MISE{}'.format(row['CodiceLocaleProgetto'].strip())

            try:
                progetto = Progetto.fullobjects.get(codice_locale=codice)
            except ObjectDoesNotExist:
                self.logger.warning(u'{}/{} - Progetto non trovato: {}. Skipping'.format(n, df_count, codice))
                report['not_found'] += 1
            else:
                progetto.descrizione = row['Sintesi'].strip()
                progetto.descrizione_fonte_nome = 'Open Data PON REC'
                progetto.descrizione_fonte_url = 'http://www.ponrec.it/open-data'
                progetto.save()

                self.logger.info(u'{}/{} - Aggiornata descrizione per il progetto: {}'.format(n, df_count, progetto))
                report['updated'] += 1

        self.logger.info(u'{updated} descrizioni aggiornate, {not_found} progetti non sono stati trovati.'.format(**report))

    @transaction.commit_on_success
    def _update_descrizioni_pongat(self, df):
        df = df[df['Sintesi intervento'].str.strip() != '']

        df_count = len(df)

        report = {'updated': 0, 'not_found': 0, 'duplicated': 0}

        for n, (index, row) in enumerate(df.iterrows(), 1):
            codice = row['CUP'].strip()

            try:
                progetto = Progetto.fullobjects.get(cup=codice)
            except ObjectDoesNotExist:
                self.logger.warning(u'{}/{} - Progetto non trovato: {}. Skipping'.format(n, df_count, codice))
                report['not_found'] += 1
            except MultipleObjectsReturned:
                self.logger.warning(u'{}/{} - Più progetti con codice: {}. Skipping'.format(n, df_count, codice))
                report['duplicate'] += 1
            else:
                progetto.descrizione = row['Sintesi intervento'].strip()
                progetto.descrizione_fonte_nome = 'Open Data PON GAT'
                progetto.descrizione_fonte_url = 'http://www.agenziacoesione.gov.it/it/pongat/comunicazione/elenco_beneficiari/index.html'
                progetto.save()

                self.logger.info(u'{}/{} - Aggiornata descrizione per il progetto: {}'.format(n, df_count, progetto))
                report['updated'] += 1

        self.logger.info(u'{updated} descrizioni aggiornate, {not_found} progetti non sono stati trovati, {duplicated} progetti si riferiscono a un CUP non univoco.'.format(**report))
