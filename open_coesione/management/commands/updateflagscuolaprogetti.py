# -*- coding: utf-8 -*-
import datetime
import logging
import zipfile
from optparse import make_option
from cStringIO import StringIO

import pandas as pd

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from progetti.models import *


class Command(BaseCommand):
    """
    Progetti related to MIUR opendata get their scuola_flag set to True.
    Data are read from oc-ext-miur/media/opendata/interventi_scuole_tot.zip compressed csv file.
    """
    help = 'Update scuola_flag field in Progetti'

    option_list = BaseCommand.option_list + (
        make_option('--progetti-zip-path',
                    dest='progetti_zip_path',
                    default='/Users/gu/Workspace/oc/oc-miur/media/open-data/interventi_scuole_tot.zip',
                    help='Select interventi zipped file, used for input'),
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

        csvfile = options['progetti_zip_path']
        dryrun = options['dryrun']

        try:
            self.logger.info(u'Reading file {} ....'.format(csvfile))

            with zipfile.ZipFile(csvfile) as zfile:
                csv = zfile.read(zfile.namelist().pop(0))
        except IOError:
            self.logger.error(u'It was impossible to open file {}'.format(csvfile))
        else:
            df_progetti = pd.read_csv(
                StringIO(csv.decode('utf-8-sig').encode('utf-8')),
                sep=';',
                encoding='utf-8',
            )

            self.logger.info(u'Done.')

            start_time = datetime.datetime.now()

            df_progetti_cod = df_progetti['COD_LOCALE_PROGETTO'].unique()

            df_count = len(df_progetti_cod)

            for n, cod in enumerate(df_progetti_cod, 1):
                try:
                    progetto = Progetto.objects.get(codice_locale=cod)
                    progetto.scuola_flag = True
                    if not dryrun:
                        progetto.save()
                    self.logger.info(u'{}/{} - Progetto: {} aggiornato'.format(n, df_count, cod))
                except ObjectDoesNotExist:
                    self.logger.warning(u'{}/{} - Progetto non trovato: {}, skipping'.format(n, df_count, cod))
                    continue

            duration = datetime.datetime.now() - start_time
            seconds = round(duration.total_seconds())

            self.logger.info(u'Fine. Tempo di esecuzione: {:02d}:{:02d}:{:02d}.'.format(int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)))
