# coding=utf-8
"""
Questo comando legge il file dei dati di contesto ISTAT dalla location interna:

    http://www.opencoesione.gov.it/opendata/Indicatori_regionali_YYYYMMDD.zip

Procedura di aggiornamento::

1. viene inoltrata una richiesta alla URL del file
2. il risultato viene letto per verificare la data di aggiornamento degli Indicatori territoriali di contesto
3. controllo se la data è diversa da quella dell'ultimo aggiornamento fatto
4. viene scaricato l'archivio e opportunamente suddiviso nella cartella dei dati

3.a il file risulta già importato
    1. Esco dalla procedura

"""
import glob
import logging
import os
import re
from StringIO import StringIO
import csvkit
import zipfile
from optparse import make_option

from django.conf import settings
from django.core.management import BaseCommand, CommandError

# ISTAT resource as URL

# paths
OPEN_DATA_PATH = os.path.join(settings.MEDIA_ROOT, "open_data")
CURRENT = os.path.join(OPEN_DATA_PATH, '.current_istat_zip') # keeps info on the lates istat archive processed

DPS_ENCODING = 'ISO-8859-1'

STATIC_PATH = os.path.join(settings.PROJECT_ROOT, "static", "csv")
static = lambda *x: os.path.join(STATIC_PATH, *x)
REGIONS_CSV_FILE = 'regioni.csv'
REGIONS_CSV = static(REGIONS_CSV_FILE)
TOPIC_CSV_FILE = 'temi.csv'
TOPIC_CSV = static(TOPIC_CSV_FILE)
INDEXES_PATH = static('indicatori')
static_topic = lambda x: os.path.join(INDEXES_PATH, "{0}.csv".format(x))
TOPIC_INDEXES_PATH = static('temaind')
static_topic_index = lambda t, i: os.path.join(TOPIC_INDEXES_PATH, "{0}_{1}.csv".format(t, i))

REQUIRED_PATHS = [OPEN_DATA_PATH, STATIC_PATH, INDEXES_PATH, TOPIC_INDEXES_PATH]

# csv fields
CSV_CODE = "COD_INDICATORE"
CSV_TOPIC = "DPS_TEMA_SINTETICO"
CSV_LOCATION = "ID_RIPARTIZIONE"
CSV_LOCATION_DESCRIPTION = "DESCRIZIONE_RIPARTIZIONE"
CSV_YEAR = "ANNO_RIFERIMENTO"
CSV_VALUE = "VALORE"
CSV_TITLE = "TITOLO"
CSV_SUBTITLE = "SOTTOTITOLO"
CSV_COLUMNS = (CSV_CODE, CSV_TITLE, CSV_SUBTITLE, "UNITA_MISURA", "ID_TEMA1",
               "DESCRIZIONE_TEMA1", "ID_TEMA2", "DESCRIZIONE_TEMA2", "ID_PRIORITA",
               "DESCRIZIONE_PRIORITA_QSN", "ID_ASSE", "DESCRIZIONE_ASSE_QCS",
               CSV_LOCATION, CSV_LOCATION_DESCRIPTION, CSV_YEAR, CSV_VALUE,
               CSV_TOPIC)

# elaboration helpers
VALID_INDEXES = settings.INDICATORI_VALIDI
VALID_REGIONS = range(1, 21) + [23]
VALID_TOPIC_IDS_BY_NAME = settings.TEMI_DB_MAPPING


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
            confirm = raw_input(u"""
Directory structure is not already created:
{0}
Try to create now?

Type 'yes' to continue, or 'no' to cancel: """.format("\n".join(REQUIRED_PATHS)))

            if confirm != 'yes':
                raise CommandError("Create static paths: \n{0}".format("\n".join(REQUIRED_PATHS)))

            for path in REQUIRED_PATHS:
                if not os.path.isdir(path):
                    os.makedirs(path)

        FORCE_UPDATE = options.get('forceupdate')

        latest_istat_archive_file_path = glob.glob(
            os.path.join(OPEN_DATA_PATH, "Indicatori_regionali_*.zip")
        )[-1]

        current_istat_archive_file_path = ""
        if os.path.isfile(CURRENT):
            with open(CURRENT, 'r') as current:
                # read content of .current file
                current_istat_archive_file_path = current.read()

        archive_processed = (current_istat_archive_file_path == latest_istat_archive_file_path)
        if archive_processed and not FORCE_UPDATE:
            self.logger.info("Archive '{0}' has been already processed. \n"
                              "No updates availables. Use --force-update to re-process\n".format(latest_istat_archive_file_path))
            return

        self.process_archive(latest_istat_archive_file_path)

        with open(CURRENT, 'w') as current:
            # update .current file
            current.write(latest_istat_archive_file_path)

        if options.get('collectstatic'):
            # if everything ok collect-static
            from django.core import management
            management.call_command('collectstatic', interactive=False, verbosity=verbosity)

    def process_archive(self, archive_path, encoding=DPS_ENCODING):
        """Directly uncompress the content of the zipped archive
           and process it, splitting the information, and writing CSV files
        """
        self.logger.info("Process archive: {0}\n".format(archive_path))

        zfile = zipfile.ZipFile(archive_path)
        # archive contains only one file
        csv_stream = zfile.read(zfile.namelist().pop(0)).decode(encoding).encode('utf8')
        self.split_csv(csv_stream)
        zfile.close()



    def split_csv(self, csv_stream):
        """Load in memory parsed csv informations.
        Then execute write_files() and clean memory.
        """
        # prepare supporting data structures
        self.db = Storage()

        reader = csvkit.CSVKitDictReader(StringIO(csv_stream), delimiter=';')

        # check if is valid headers
        headers_diff = set(CSV_COLUMNS).symmetric_difference(set(reader.fieldnames))
        if headers_diff:
            raise CommandError("Invalid columns format. The differences are: {0}".format(
                headers_diff
            ))

        for i, row in enumerate(reader):

            # skip not allowed index
            if not row.get(CSV_CODE).strip() in VALID_INDEXES:
                continue

            region_id = self.read_region(row)

            # skip if not in VALID_REGIONS
            if not region_id:
                continue

            # read topic
            topic_id = self.read_topic(row)

            # read index
            index_id, year, value = self.read_index_value(row)

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

        # clean memory
        del self.db

    def read_region(self, row):
        location_id = int(row.get(CSV_LOCATION).strip())
        if location_id not in VALID_REGIONS:
            return False
        if location_id not in self.db.regions:
            # add this region to database
            self.db.regions[location_id] = row.get(CSV_LOCATION_DESCRIPTION)
        return location_id

    def read_topic(self, row):
        topic_name = row.get(CSV_TOPIC).strip()
        # try to load this topic from mapping
        topic_id = VALID_TOPIC_IDS_BY_NAME.get(topic_name)
        if topic_id not in self.db.topics:
            # add this topic to database
            self.db.topics[topic_id] = topic_name
        return topic_id

    def read_index_value(self, row):
        index_id = row.get(CSV_CODE).strip()
        year = int(row.get(CSV_YEAR))

        if index_id not in self.db.indexes:
            # add this index to database
            self.db.indexes[index_id] = {
                'title': row.get(CSV_TITLE),
                'subtitle': row.get(CSV_SUBTITLE)
            }

        value = row.get(CSV_VALUE) or None

        if value:
            # clean string
            value = re.sub(r'[^\d,.]', '', value)
            # split for avoid thousand separator and different locale comma/dot symbol
            parts = re.split(r'[,.]', value)
            if len(parts) == 1:
                float_str = parts[0]
            else:
                float_str = "{0}.{1}".format(''.join(parts[0:-1]), parts[-1])
            value = float(float_str)

        return index_id, year, value

    def write_files(self):
        """From memory informations (self.db) creates all required csv files.
        """
        regions_fieldnames = [u'ID', u'Denominazione regione']
        topic_columns = [u'ID', u'Denominazione tema sintetico']
        index_columns = [u'ID', u'Titolo', u'Sottotitolo']
        topic_index_columns = [u'Regione'] + [unicode(x) for x in self.db.years]

        self.logger.info("Writing {0} regions\n".format(len(self.db.regions)))
        with open(REGIONS_CSV, 'wb') as csv_file:
            writer = csvkit.CSVKitDictWriter(csv_file, regions_fieldnames)
            writer.writeheader()

            for location_id in sorted(self.db.regions):
                writer.writer.writerow([unicode(location_id), self.db.regions.get(location_id)])
            self.logger.info(u"{0}\n".format(u", ".join(self.db.regions.values())))

        self.logger.info('Writing {0} topics\n'.format(len(self.db.topics)))
        with open(TOPIC_CSV, 'wb') as csv_file:
            writer = csvkit.CSVKitDictWriter(csv_file, topic_columns)
            writer.writeheader()

            for topic_id in sorted(self.db.topics):
                writer.writer.writerow([unicode(topic_id), self.db.topics.get(topic_id)])

        for topic_id in sorted(self.db.indexes_by_topic):
            self.logger.info(u"[{0}] {1}\n".format(topic_id, self.db.topics.get(topic_id)).encode('utf-8'))

            with open(static_topic(topic_id), 'wb') as csv_file:
                writer = csvkit.CSVKitDictWriter(csv_file, regions_fieldnames)
                writer.writeheader()

                for index_id in sorted(self.db.indexes_by_topic.get(topic_id)):
                    index = self.db.indexes[index_id]
                    self.logger.debug(
                        u"\n[{0}] [{1}] {2}\n    {3}".format(
                            topic_id, index_id, index.get('title'), index.get('subtitle')))
                    writer.writer.writerow([unicode(index_id), index.get('title'), index.get('subtitle')])

                    with open(static_topic_index(topic_id, index_id), 'wb') as csv_index_file:
                        index_writer = csvkit.CSVKitDictWriter(csv_index_file, topic_index_columns)
                        index_writer.writeheader()

                        for location_id in sorted(self.db.values.get(index_id)):
                            values = [self.db.regions[location_id], ]
                            # collect values
                            for year in self.db.values.get(index_id).get(location_id):
                                val = self.db.values.get(index_id).get(location_id).get(year)
                                values.append(str(val) if val else '')

                            index_writer.writer.writerow(values)
