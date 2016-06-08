# -*- coding: utf-8 -*-
import logging
import os
import re
from django.db import transaction
import pandas as pd
import zipfile
import urllib2
from optparse import make_option
from cStringIO import StringIO

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from progetti.models import Tema
from open_coesione.charts.models import Indicatore, IndicatoreRegionale, Ripartizione

# ISTAT resource as URL
ISTAT_ARCHIVE_FILE_PATH = 'http://www.istat.it/storage/politiche-sviluppo/Archivio_unico_indicatori_regionali.zip'
ISTAT_FILE_NAME = 'Archivio_unico_indicatori_regionali.csv'
# ISTAT_FILE_ENCODING = 'utf-8-sig'
ISTAT_FILE_ENCODING = 'latin1'

# csv fields
CSV_CODE = 'COD_INDICATORE'
CSV_TOPIC = 'OC_TEMA_SINTETICO'
CSV_LOCATION = 'ID_RIPARTIZIONE'
CSV_LOCATION_DESCRIPTION = 'DESCRIZIONE_RIPARTIZIONE'
CSV_YEAR = 'ANNO_RIFERIMENTO'
CSV_VALUE = 'VALORE'
CSV_TITLE = 'TITOLO'
CSV_SUBTITLE = 'SOTTOTITOLO'

CSV_REQUIRED_COLUMNS = (CSV_CODE, CSV_TITLE, CSV_SUBTITLE, CSV_LOCATION, CSV_LOCATION_DESCRIPTION, CSV_YEAR, CSV_VALUE, CSV_TOPIC)

# elaboration helpers
VALID_INDEXES = settings.INDICATORI_VALIDI
VALID_REGIONS = range(1, 21) + [23]

CURRENT = os.path.join(settings.REPO_ROOT, '.current_istat_zip')  # keeps info on the latest istat archive processed


def convert_topic(topic):
    topic_map = {
        u'Rinnovamento urbano e rurale': u'Rinnovamento urbano  e rurale',
        u'Rafforzamento delle capacità della PA': u'Rafforzamento capacità della PA',
    }

    topic = topic.strip()
    return topic_map[topic] if topic in topic_map else topic


def convert_value(value):
    # clean string
    value = re.sub(r'[^\d,.]', '', value).strip(',.')
    if value:
        # split for avoid thousand separator and different locale comma/dot symbol
        parts = re.split(r'[,.]', value)
        if len(parts) == 1:
            float_str = parts[0]
        else:
            float_str = '{}.{}'.format(''.join(parts[0:-1]), parts[-1])
        value = float(float_str)
        value = str(value)

    return value


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--force-update',
                    dest='forceupdate',
                    default=False,
                    action='store_true',
                    help='Force extraction of archive'),
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

        try:
            request = urllib2.Request(ISTAT_ARCHIVE_FILE_PATH)

            if not options.get('forceupdate'):
                request.add_header('If-None-Match', self.stored_etag)

            archivefile = urllib2.urlopen(request)
        except (urllib2.HTTPError, Exception) as e:
            if isinstance(e, urllib2.HTTPError) and e.code == 304:
                self.logger.debug(u'Archivio già elaborato. Nessun aggiornamento disponibile. Usare --force-update per rielaborare')
            else:
                self.logger.error(e)
        else:
            try:
                self.process_archive(archivefile)
            except Exception as e:
                self.logger.error(e)
            else:
                self.stored_etag = archivefile.headers['etag']

    def process_archive(self, archivefile):
        self.logger.debug(u'Elaborazione archivio: {0}'.format(archivefile.url))

        buffer = StringIO(archivefile.read())
        zfile = zipfile.ZipFile(buffer)
        # csv_stream = zfile.read(ISTAT_FILE_NAME)
        csv_stream = zfile.read([filename for filename in zfile.namelist() if filename.endswith('.csv')][0])
        self.split_csv(csv_stream)
        zfile.close()

    @transaction.commit_manually
    def split_csv(self, csv_stream):
        df = pd.read_csv(
            StringIO(csv_stream),
            sep=';',
            # sep='\t',
            header=0,
            low_memory=True,
            dtype=object,
            encoding=ISTAT_FILE_ENCODING,
            keep_default_na=False,
            converters={
                CSV_CODE: lambda x: x.strip().zfill(3),
                CSV_LOCATION: lambda x: int(x.strip()),
                CSV_TOPIC: convert_topic,
                CSV_VALUE: convert_value,
                CSV_YEAR: lambda x: int(x.strip()),
            },
        )

        # check if is valid headers
        headers_diff = set(CSV_REQUIRED_COLUMNS).difference(set(df))
        if headers_diff:
            raise CommandError(u'Formato colonne non valido. Le colonne mancanti sono: {}'.format(list(headers_diff)))

        tema_desc2obj = {o.descrizione: o for o in Tema.objects.principali()}

        df_i = df[[CSV_CODE, CSV_TITLE, CSV_SUBTITLE, CSV_TOPIC]].drop_duplicates()
        df_i_count = len(df_i)

        for n, (index, row) in enumerate(df_i.iterrows(), 1):
            obj = self.get_and_update_or_create(u'{}/{}'.format(n, df_i_count), Indicatore, codice=row[CSV_CODE], defaults={'titolo': row[CSV_TITLE], 'sottotitolo': row[CSV_SUBTITLE], 'tema': tema_desc2obj[row[CSV_TOPIC]]})

        transaction.commit()

        df_r = df[[CSV_LOCATION, CSV_LOCATION_DESCRIPTION]].drop_duplicates()
        df_r_count = len(df_r)

        for n, (index, row) in enumerate(df_r.iterrows(), 1):
            obj = self.get_and_update_or_create(u'{}/{}'.format(n, df_r_count), Ripartizione, id=row[CSV_LOCATION], defaults={'descrizione': row[CSV_LOCATION_DESCRIPTION]})

        transaction.commit()

        IndicatoreRegionale.objects.update(da_eliminare=True)
        transaction.commit()

        df = df[df[CSV_CODE].isin(VALID_INDEXES) & df[CSV_LOCATION].isin(VALID_REGIONS) & df[CSV_TOPIC].isin(tema_desc2obj)]
        df_count = len(df)

        for n, (index, row) in enumerate(df.iterrows(), 1):
            obj = self.get_and_update_or_create(u'{}/{}'.format(n, df_count), IndicatoreRegionale, indicatore_id=row[CSV_CODE], ripartizione_id=row[CSV_LOCATION], anno=row[CSV_YEAR], defaults={'valore': row[CSV_VALUE]})

            obj.da_eliminare = False
            obj.save()

            if (n % 5000 == 0) or (n == df_count):
                transaction.commit()

        da_eliminare = IndicatoreRegionale.objects.filter(da_eliminare=True)
        da_eliminare_count = len(da_eliminare)

        for n, obj in enumerate(da_eliminare, 1):
            obj.delete()
            self.logger.info(u'{}/{} - Eliminato {}: {}'.format(n, da_eliminare_count, IndicatoreRegionale._meta.verbose_name_raw, obj))

        transaction.commit()

    @property
    def stored_etag(self):
        try:
            with open(CURRENT, 'r') as current:
                value = current.read()
        except EnvironmentError:
            value = ''

        return value

    @stored_etag.setter
    def stored_etag(self, value):
        with open(CURRENT, 'w') as current:
            current.write(value)

    def get_and_update_or_create(self, baselog, model, **kwargs):
        obj, created = model.objects.get_or_create(**kwargs)

        defaults = kwargs.get('defaults', {})
        if created:
            self.logger.info(u'{} - Creato {}: {}'.format(baselog, model._meta.verbose_name_raw, obj))
        elif all([getattr(obj, k) == v for k, v in defaults.iteritems()]):
            self.logger.debug(u'{} - Trovato {}: {}'.format(baselog, model._meta.verbose_name_raw, obj))
        else:
            obj_old = unicode(obj)
            for k, v in defaults.iteritems():
                setattr(obj, k, v)
            obj.save()
            self.logger.info(u'{} - Modificato {}: {} -> {}'.format(baselog, model._meta.verbose_name_raw, obj_old, obj))

        return obj
