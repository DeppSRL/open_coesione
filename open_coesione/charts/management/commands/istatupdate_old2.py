# -*- coding: utf-8 -*-
import logging
import os
import re
import pandas as pd
import csvkit
import zipfile
import urllib2
from optparse import make_option
from cStringIO import StringIO

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from progetti.models import Tema

# ISTAT resource as URL
ISTAT_ARCHIVE_FILE_PATH = 'http://www.istat.it/storage/politiche-sviluppo/Archivio_unico_indicatori_regionali.zip'
ISTAT_FILE_NAME = 'Archivio_unico_indicatori_regionali.csv'
# ISTAT_FILE_ENCODING = 'ISO-8859-1'
ISTAT_FILE_ENCODING = 'utf-8-sig'

# paths
STATIC_PATH = os.path.join(settings.PROJECT_ROOT, 'static', 'csv')
static = lambda *x: os.path.join(STATIC_PATH, *x)
REGIONS_CSV_FILE = 'regioni.csv'
REGIONS_CSV = static(REGIONS_CSV_FILE)
TOPICS_CSV_FILE = 'temi.csv'
TOPICS_CSV = static(TOPICS_CSV_FILE)
INDEXES_PATH = static('indicatori')
static_topic = lambda t: os.path.join(INDEXES_PATH, '{0}.csv'.format(t))
TOPIC_INDEXES_PATH = static('temaind')
static_topic_index = lambda t, i: os.path.join(TOPIC_INDEXES_PATH, '{0}_{1}.csv'.format(t, i))

REQUIRED_PATHS = [STATIC_PATH, INDEXES_PATH, TOPIC_INDEXES_PATH]

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
# VALID_TOPIC_IDS_BY_NAME = settings.TEMI_DB_MAPPING
VALID_TOPIC_IDS_BY_NAME = {tema.descrizione: int(tema.codice) for tema in Tema.objects.principali()}

CURRENT = os.path.join(STATIC_PATH, '.current_istat_zip')  # keeps info on the latest istat archive processed


def convert_topic(topic):
    topic_map = {
        u'Rinnovamento urbano e rurale': u'Rinnovamento urbano  e rurale',
        u'Rafforzamento delle capacità della PA': u'Rafforzamento capacità della PA',
    }

    topic = topic.strip()
    return topic_map[topic] if topic in topic_map else topic


class Storage(object):
    def __init__(self):
        self.regions = {}
        self.topics = {}
        self.indexes = {}
        self.values = {}
        self.years = []
        self.indexes_by_topic = {}


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--force-update',
                    dest='forceupdate',
                    default=False,
                    action='store_true',
                    help='Force extraction of archive'),
        make_option('--collectstatic',
                    dest='collectstatic',
                    default=False,
                    action='store_true',
                    help='Collect static at the end of process'),
    )
    logger = logging.getLogger('csvimport')

    db = Storage()

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

        # check if paths exists
        if not all(map(os.path.exists, REQUIRED_PATHS)):
            confirm = raw_input(u"\nDirectory structure is not already created:\n{0}\nTry to create now?\n\nType 'yes' to continue, or 'no' to cancel: ".format('\n'.join(REQUIRED_PATHS)))

            if confirm == 'yes':
                for path in REQUIRED_PATHS:
                    if not os.path.isdir(path):
                        os.makedirs(path)
            else:
                exit(1)

        try:
            request = urllib2.Request(ISTAT_ARCHIVE_FILE_PATH)

            if not options.get('forceupdate'):
                request.add_header('If-None-Match', self.stored_etag)

            archivefile = urllib2.urlopen(request)
        except (urllib2.HTTPError, Exception) as e:
            if isinstance(e, urllib2.HTTPError) and e.code == 304:
                self.logger.info('Archive has been already processed. No updates availables. Use --force-update to re-process')
            else:
                self.logger.error(e)
        else:
            try:
                self.process_archive(archivefile)
            except Exception as e:
                self.logger.error(e)
            else:
                self.stored_etag = archivefile.headers['etag']

                if options.get('collectstatic'):
                    from django.core import management
                    management.call_command('collectstatic', interactive=False, verbosity=verbosity)

    def process_archive(self, archivefile):
        """Directly uncompress the content of the zipped archive
        and process it, splitting the information, and writing CSV files
        """
        self.logger.info(u'Process archive: {0}'.format(archivefile.url))

        buffer = StringIO(archivefile.read())
        zfile = zipfile.ZipFile(buffer)
        csv_stream = zfile.read(ISTAT_FILE_NAME)
        self.split_csv(csv_stream)
        zfile.close()

    def split_csv(self, csv_stream):
        """Load in memory parsed csv informations.
        Then execute write_files() and clean memory.
        """
        df = pd.read_csv(
            StringIO(csv_stream),
            sep=';',
            header=0,
            low_memory=True,
            dtype=object,
            encoding=ISTAT_FILE_ENCODING,
            keep_default_na=False,
            converters={
                CSV_CODE: lambda x: x.strip().zfill(3),
                CSV_LOCATION: lambda x: int(x.strip()),
                CSV_TOPIC: convert_topic,
                CSV_VALUE: lambda x: x.strip(' .-'),
                CSV_YEAR: lambda x: int(x.strip()),
            },
        ).sort([CSV_YEAR, CSV_CODE, CSV_LOCATION])

        # check if is valid headers
        headers_diff = set(CSV_REQUIRED_COLUMNS).difference(set(df))
        if headers_diff:
            raise CommandError(u'Invalid columns format. Missing columns are: {0}'.format(list(headers_diff)))

        for i, row in df.iterrows():
            # skip not allowed index
            if not row.get(CSV_CODE) in VALID_INDEXES:
                self.logger.debug(u'Skipping {COD_INDICATORE} - {OC_TEMA_SINTETICO} {DESCRIZIONE_RIPARTIZIONE}/{ANNO_RIFERIMENTO}'.format(**row))
                continue

            # read region
            region_id = self.read_region(row)

            # skip if not in VALID_REGIONS
            if not region_id:
                self.logger.debug(u'Skipping {COD_INDICATORE} - {OC_TEMA_SINTETICO} {DESCRIZIONE_RIPARTIZIONE}/{ANNO_RIFERIMENTO}'.format(**row))
                continue

            # read topic
            topic_id = self.read_topic(row)

            # skip if not in VALID_TOPIC_IDS_BY_NAME
            if not topic_id:
                self.logger.debug(u'Skipping {COD_INDICATORE} - {OC_TEMA_SINTETICO} {DESCRIZIONE_RIPARTIZIONE}/{ANNO_RIFERIMENTO}'.format(**row))
                continue

            # read index
            index_id, year, value = self.read_index_value(row)
            self.logger.debug(u'Parsing {COD_INDICATORE} - {OC_TEMA_SINTETICO}({0}) - {DESCRIZIONE_RIPARTIZIONE}({1})/{ANNO_RIFERIMENTO} - {VALORE}'.format(topic_id, region_id, **row))

            # initialize database for indexes of this topic
            if not topic_id in self.db.indexes_by_topic:
                self.db.indexes_by_topic[topic_id] = []

            # initialize database for indexes grouped by topics
            if not index_id in self.db.indexes_by_topic[topic_id]:
                self.db.indexes_by_topic[topic_id].append(index_id)

            # initialize database for this year
            if not year in self.db.years:
                self.db.years.append(year)

            # initialize database for this index
            if not index_id in self.db.values:
                self.db.values[index_id] = {}

            # initialize database with this region with this index
            if not region_id in self.db.values[index_id]:
                self.db.values[index_id][region_id] = {}

            # finally, add this index value to database
            self.db.values[index_id][region_id][year] = value

        # write splitted csv files
        self.write_files()

    def read_region(self, row):
        location_id = row.get(CSV_LOCATION)
        if location_id not in VALID_REGIONS:
            return False
        if location_id not in self.db.regions:
            # add this region to database
            self.db.regions[location_id] = row.get(CSV_LOCATION_DESCRIPTION)
        return location_id

    def read_topic(self, row):
        topic_name = row.get(CSV_TOPIC)
        if topic_name not in VALID_TOPIC_IDS_BY_NAME:
            return False
        topic_id = VALID_TOPIC_IDS_BY_NAME.get(topic_name)
        if topic_id not in self.db.topics:
            # add this topic to database
            self.db.topics[topic_id] = topic_name
        return topic_id

    def read_index_value(self, row):
        index_id = row.get(CSV_CODE)
        year = row.get(CSV_YEAR)

        if index_id not in self.db.indexes:
            # add this index to database
            self.db.indexes[index_id] = {
                'title': row.get(CSV_TITLE),
                'subtitle': row.get(CSV_SUBTITLE)
            }

        value = row.get(CSV_VALUE, None)

        if value:
            # clean string
            value = re.sub(r'[^\d,.]', '', value)
            # split for avoid thousand separator and different locale comma/dot symbol
            parts = re.split(r'[,.]', value)
            if len(parts) == 1:
                float_str = parts[0]
            else:
                float_str = '{0}.{1}'.format(''.join(parts[0:-1]), parts[-1])
            value = float(float_str)

        return index_id, year, value

    def write_files(self):
        """From memory informations (self.db) creates all required csv files.
        """
        regions_columns = [u'ID', u'Denominazione regione']
        topic_columns = [u'ID', u'Denominazione tema sintetico']
        index_columns = [u'ID', u'Titolo', u'Sottotitolo']
        topic_index_columns = [u'Regione'] + [unicode(year) for year in self.db.years]

        self.logger.info(u'Writing {0} regions: {1}'.format(len(self.db.regions), self.db.regions.values()))
        with open(REGIONS_CSV, 'wb') as csv_file:
            writer = csvkit.CSVKitDictWriter(csv_file, regions_columns)
            writer.writeheader()

            for location_id in sorted(self.db.regions):
                writer.writer.writerow([unicode(location_id), self.db.regions.get(location_id)])

        self.logger.info(u'Writing {0} topics: {1}'.format(len(self.db.topics), self.db.topics.values()))
        with open(TOPICS_CSV, 'wb') as csv_file:
            writer = csvkit.CSVKitDictWriter(csv_file, topic_columns)
            writer.writeheader()

            for topic_id in sorted(self.db.topics):
                writer.writer.writerow([unicode(topic_id), self.db.topics.get(topic_id)])

        for topic_id in sorted(self.db.indexes_by_topic):
            self.logger.info(u'[{0}] {1}'.format(topic_id, self.db.topics.get(topic_id)))

            with open(static_topic(topic_id), 'wb') as csv_file:
                writer = csvkit.CSVKitDictWriter(csv_file, index_columns)
                writer.writeheader()

                for index_id in sorted(self.db.indexes_by_topic.get(topic_id)):
                    index = self.db.indexes.get(index_id)
                    self.logger.info(u' |-[{0}-{1}] {2}'.format(topic_id, index_id, index.get('title')))
                    writer.writer.writerow([unicode(index_id), index.get('title'), index.get('subtitle')])

                    with open(static_topic_index(topic_id, index_id), 'wb') as csv_index_file:
                        index_writer = csvkit.CSVKitDictWriter(csv_index_file, topic_index_columns)
                        index_writer.writeheader()

                        for location_id in sorted(self.db.values.get(index_id)):
                            values = [self.db.regions.get(location_id)] + [self.db.values.get(index_id).get(location_id).get(year, '') for year in self.db.years]
                            index_writer.writer.writerow(values)

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
