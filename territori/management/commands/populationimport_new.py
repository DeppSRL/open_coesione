# -*- coding: utf-8 -*-
import datetime
import json
import logging
import pandas as pd
import re
import zipfile
from collections import OrderedDict
from cStringIO import StringIO
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import DatabaseError, IntegrityError
from optparse import make_option
from progetti.models import Progetto, ProgettoDeliberaCIPE, DeliberaCIPE, Ruolo, Localizzazione, PagamentoProgetto,\
    ProgrammaAsseObiettivo, ProgrammaLineaAzione, ClassificazioneAzione, ClassificazioneOggetto, ClassificazioneQSN,\
    Tema, Fonte
from soggetti.models import Soggetto
from territori.models import Territorio


class Command(BaseCommand):
    """
    Data are imported from their CSV sources.
    """
    help = 'Import population data from csv'

    option_list = BaseCommand.option_list + (
        make_option('--zip-file',
                    dest='zip_file',
                    default='./all',
                    help='Select zipped csv file'),
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

        zip_file = options['zip_file']

        try:
            self.logger.info(u'Reading file {} ....'.format(zip_file))

            with zipfile.ZipFile(zip_file) as zfile:
                csv = zfile.read(zfile.namelist().pop(0))
        except IOError:
            self.logger.error(u'It was impossible to open file {}'.format(zip_file))
        else:
            df = pd.read_csv(
                StringIO(csv),
                sep='|',
                header=0,
                low_memory=True,
                dtype=object,
                converters={},
            )

            self.logger.info(u'Done.')

            df = df[['ITTER107', 'Territorio', 'SEXISTAT1', 'Sesso', 'Value']][(df['ETA1'] == 'TOTAL') & (df['CITTADINANZA'] == 'TOTAL') & (df['TIME'] == '2011')].sort(['ITTER107', 'SEXISTAT1']).groupby('ITTER107', as_index=False)[['Sesso', 'Value']].aggregate(lambda x: x.tolist())

            self.logger.info(u'Inizio import.')

            start_time = datetime.datetime.now()

            df_count = len(df)

            for n, (index, row) in enumerate(df.iterrows(), 1):
                values = dict(zip(row['Sesso'], map(int, row['Value'])))
                print('{}/{}: {} ({})'.format(n, df_count, row['ITTER107'], values))

            duration = datetime.datetime.now() - start_time
            seconds = round(duration.total_seconds())

            self.logger.info(u'Fine. Tempo di esecuzione: {:02d}:{:02d}:{:02d}.'.format(int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)))
