# -*- coding: utf-8 -*-
from collections import OrderedDict
import logging
from optparse import make_option
import os
import zipfile

import pandas as pd

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from progetti.models import *


class Command(BaseCommand):
    """
    Progetti related to MIUR opendata get their scuola_flag set to True.
    Data are read from oc-ext-miur/media/opendata/interventi_scuole_tot.zip
    compressed csv file.
    """
    help = "Update scuola_flag field in Progetti"

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


        progetti_zip_path = options['progetti_zip_path']

        dryrun = options['dryrun']

        # unzip CSV progetti file and
        # load OC progetti data (45 sec)
        self.logger.debug('- unzipping progetti')
        zip_ref = zipfile.ZipFile(progetti_zip_path, 'r')
        zip_ref.extractall(os.path.dirname(progetti_zip_path))
        zip_ref.close()
        self.logger.info('- progetti file unzipped')

        progetti_csv_path = progetti_zip_path.replace('.zip','.csv')

        self.logger.debug('- reading progetti from CSV')
        df_progetti = pd.read_csv(
            progetti_csv_path,
            sep=";", encoding='utf-8-sig'
        )
        self.logger.info('- progetti read from CSV')

        df_progetti_cod = df_progetti['COD_LOCALE_PROGETTO'].unique()
        os.remove(progetti_csv_path)

        n = 0
        n_tot = len(df_progetti_cod)
        for cod in df_progetti_cod:
            n += 1
            try:
                progetto = Progetto.objects.get(codice_locale=cod)
                progetto.scuola_flag = True
                if not dryrun:
                    progetto.save()
                self.logger.info("%s/%s - Progetto: %s aggiornato" % (n, n_tot, cod))
            except ObjectDoesNotExist:
                self.logger.warning("%s/%s - Progetto non trovato: %s, skipping" % (n, n_tot, cod))
                continue

        self.logger.info("Fine")






