# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction
from django.db.utils import DatabaseError, IntegrityError
from django.core.management.base import BaseCommand

from optparse import make_option

import re
import pandas as pd
import datetime

from progetti.models import *
from soggetti.models import *
from territori.models import Territorio


class Command(BaseCommand):
    """
    Data are imported from their CSV sources.
    """
    help = 'Import data from csv'

    import_types = {
        'localizzazioni': {
            'files': ['localizzazioni_FSC0713_{0}.csv', 'localizzazioni_FS0713_{0}.csv', 'localizzazioni_PAC_{0}.csv', 'localizzazioni_CIPE_{0}.csv', 'loc_inattivi_{0}.csv'],
            'import_method': '_import_localizzazioni',
            'converters': None,
        },
    }

    option_list = BaseCommand.option_list + (
        make_option('--csv-path',
                    dest='csv_path',
                    default=None,
                    help='Select csv files path.'),
        make_option('--csv-date',
                    dest='csv_date',
                    default=None,
                    help='Date of data.'),
        make_option('--import-type',
                    dest='import_type',
                    default=None,
                    help='Type of import; select among {0}.'.format(', '.join(['"' + t + '"' for t in import_types]))),
        make_option('--append',
                    dest='append',
                    action='store_true',
                    help='If not set, delete records before importing new.'),
        make_option('--encoding',
                    dest='encoding',
                    default='utf-8',
                    help='Set character encoding of input file.'),
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

        df = pd.DataFrame()

        csvpath = options['csv_path']
        csvdate = options['csv_date']
        importtype = options['import_type']

        if not importtype in self.import_types:
            self.logger.error(u'Wrong type "{0}". Select among {1}.'.format(importtype, ', '.join(['"' + t + '"' for t in self.import_types])))
            exit(1)

        # read csv files
        for file in self.import_types[importtype]['files']:
            csvfile = csvpath.rstrip('/') + '/' + file.format(csvdate)

            self.logger.info(u'Reading file {0} ....'.format(csvfile))

            try:
                df_tmp = pd.read_csv(
                    csvfile,
                    sep=';',
                    header=0,
                    low_memory=True,
                    dtype=object,
                    encoding=options['encoding'],
                    keep_default_na=False,
                    converters=self.import_types[importtype]['converters'],
                )
            except IOError:
                self.logger.error(u'It was impossible to open file {0}'.format(csvfile))
                continue
            else:
                df_tmp[u'FLAG_ATTIVO'] = not ('inattivi' in file)

                df = df.append(df_tmp, ignore_index=True)

                del df_tmp

                self.logger.info(u'Done.')

        if len(df) == 0:
            self.logger.error(u'Nessun dato da processare.')
            exit(1)

        df.fillna('', inplace=True)
        df.drop_duplicates(inplace=True)

        self.logger.info(u'Inizio import "{0}" ({1}).'.format(importtype, csvdate))

        start_time = datetime.datetime.now()

        method = getattr(self, str(self.import_types[importtype]['import_method']))
        method(df, options['append'])

        duration = datetime.datetime.now() - start_time
        seconds = round(duration.total_seconds())

        self.logger.info(u'Fine. Tempo di esecuzione: {0:02d}:{1:02d}:{2:02d}.'.format(int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)))

    def _import_localizzazioni(self, df, append):
        df = df[df['DEN_COMUNE'].isin(['Tremezzina', 'Montoro'])]
        df_count = len(df)

        insert_list = []

        n = 0
        for index, row in df.iterrows():
            n += 1

            progetto_pk = self._get_value(row, 'COD_LOCALE_PROGETTO') or self._get_value(row, 'COD_DIPE')

            try:
                progetto = Progetto.fullobjects.get(pk=progetto_pk)

                self.logger.debug(u'{0}/{1} - Progetto: {2}'.format(n, df_count, progetto))

            except ObjectDoesNotExist:
                self.logger.warning(u'{0}/{1} - Progetto non trovato: {2}. Skipping.'.format(n, df_count, progetto_pk))

            else:
                territorio = None

                tipo_territorio = self._get_value(row, 'DPS_TERRITORIO_PROG')

                # per i progetti CIPE non c'è il campo DPS_TERRITORIO_PROG
                if not tipo_territorio:
                    if row['COD_PROVINCIA'] in ('000', '900'):
                        tipo_territorio = Territorio.TERRITORIO.R
                    elif row['COD_COMUNE'] in ('000', '900'):
                        tipo_territorio = Territorio.TERRITORIO.P
                    else:
                        tipo_territorio = Territorio.TERRITORIO.C

                if not tipo_territorio in dict(Territorio.TERRITORIO):
                    self.logger.warning(u'{0}/{1} - Tipo di territorio sconosciuto o errato: {2}. Skipping.'.format(n, df_count, tipo_territorio))

                else:
                    lookup = {}
                    lookup['territorio'] = tipo_territorio
                    lookup['cod_reg'] = int(row['COD_REGIONE'])

                    if tipo_territorio == Territorio.TERRITORIO.R:
                        pass
                    elif tipo_territorio == Territorio.TERRITORIO.P:
                        lookup['cod_prov'] = int(row['COD_PROVINCIA'])
                    elif tipo_territorio == Territorio.TERRITORIO.C:
                        lookup['cod_prov'] = int(row['COD_PROVINCIA'])
                        lookup['cod_com'] = '{0}{1}'.format(int(row['COD_PROVINCIA']), row['COD_COMUNE'])
                    else:
                        lookup['cod_prov'] = 0
                        lookup['cod_com'] = 0

                    try:
                        territorio = Territorio.objects.get(**lookup)

                        self.logger.debug(u'{0}/{1} - Territorio: {2}'.format(n, df_count, territorio))

                    except ObjectDoesNotExist:
                        if tipo_territorio == Territorio.TERRITORIO.C:
                            del lookup['cod_prov']
                            del lookup['cod_com']

                            lookup['denominazione'] = row['DEN_COMUNE']

                            try:
                                territorio = Territorio.objects.get(**lookup)
                                self.logger.debug(u'{0}/{1} - Territorio di tipo "Comune" individuato attraverso la denominazione: {2}.'.format(n, df_count, territorio))
                            except ObjectDoesNotExist:
                                pass

                    if not territorio:
                        self.logger.warning(u'{0}/{1} - Territorio non trovato: {2} [{3}]/{4} [{5}]/{6} [{7}] ({8}). Skipping.'.format(n, df_count, row['DEN_COMUNE'], row['COD_COMUNE'], row['DEN_PROVINCIA'], row['COD_PROVINCIA'], row['DEN_REGIONE'], row['COD_REGIONE'], tipo_territorio))

                if territorio:
                    insert_list.append(
                        Localizzazione(
                            progetto=progetto,
                            territorio=territorio,
                            indirizzo=self._get_value(row, 'INDIRIZZO_PROG'),
                            cap=self._get_value(row, 'CAP_PROG'),
                            dps_flag_cap=int(self._get_value(row, 'DPS_FLAG_CAP_PROG') or 0),
                        )
                    )
                    self.logger.info(u'{0}/{1} - Creata localizzazione progetto: {2}'.format(n, df_count, insert_list[-1]))

                    del progetto
                    del territorio

            if (n % 5000 == 0) or (n == df_count):
                self.logger.info(u'{0}/{1} -----------------> Salvataggio in corso.'.format(n, df_count))
                Localizzazione.objects.bulk_create(insert_list)
                insert_list = []

    def _log(self, created, msg):
        if created:
            self.logger.info(msg)
        else:
            self.logger.debug(msg.replace('Creat', 'Trovat'))

    @staticmethod
    def _get_value(dict, key, type='string'):
        """
        """
        if key in dict:
            dict[key] = unicode(dict[key])
            if dict[key].strip():
                value = dict[key].strip()

                if type == 'decimal':
                    value = Decimal(value.replace(',', '.'))
                elif type == 'date':
                    value = datetime.datetime.strptime(value, '%Y%m%d')

                return value

        return None
