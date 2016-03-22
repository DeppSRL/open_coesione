# -*- coding: utf-8 -*-
import logging
from django.core.management.base import BaseCommand
from django.core.cache import cache

from optparse import make_option

import pandas as pd
import datetime
import zipfile
from cStringIO import StringIO
from open_coesione.views import OpendataView


class Command(BaseCommand):
    """
    """
    help = ''

    option_list = BaseCommand.option_list + (
        make_option('--encoding',
                    dest='encoding',
                    default='utf-8-sig',
                    help='Set character encoding of input file.'),
    )

    logger = logging.getLogger(__name__)

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

        encoding = options['encoding']

        start_time = datetime.datetime.now()

        key = 'df-progetti'

        df = cache.get(key)

        if df is None:
            csvfile = OpendataView.get_latest_localfile('progetti_OC.zip')

            self.logger.info(u'Reading file {} ....'.format(csvfile))

            try:
                # with zipfile.ZipFile(csvfile) as zfile:
                #     csv = zfile.read(zfile.namelist().pop(0))

                with zipfile.ZipFile(csvfile) as z:
                    with z.open(z.filelist[0]) as f:
                        df = pd.read_csv(
                            f,
                            # OpendataView.get_latest_localfile('progetti_OC.csv'),
                            # StringIO(csv.decode(encoding).encode('utf-8')),
                            sep=';',
                            header=0,
                            low_memory=True,
                            dtype=object,
                            # encoding='utf-8',
                            encoding=encoding,
                            keep_default_na=False,
                        )
            except IOError:
                self.logger.error(u'It was impossible to open file {}'.format(csvfile))
                exit(1)
            else:
                df = df.rename(columns=lambda x: x.strip('"'))
                print(df[df['COD_LOCALE_PROGETTO'].isin(['5SI190', '5SI191', '5SI127', '5SI282', '5SI152', '1LIIM10I.08/1600/1/1', '1LIGE09-EP1/1200/1/1', '1LIIM09.II.AC/1100/11/1'])]['OC_DATA_FINE_EFFETTIVA'])
                # cache.set(key, df)
                self.logger.info(u'Done.')
        else:
            self.logger.info(u'Cached.')

        duration = datetime.datetime.now() - start_time
        seconds = round(duration.total_seconds())

        self.logger.info(u'Fine. Tempo di esecuzione: {:02d}:{:02d}:{:02d}.'.format(int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)))
