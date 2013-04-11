# coding=utf-8
"""
Questo comando si occupa di recuperare un archivio zip presente sul sito del DPS
il quale contiene gli indici statistici delle regioni.

http://www.dps.tesoro.it/opencoesione/dati_contesto.asp

L'archivio deve essere tentuto sotto osservazione per monitorarne i cambiamenti,
segnalati da parte dell'amministrazione grazie al nome del file,
nel quale é presente la data dell'ultimo aggiornamento.

http://www.dps.tesoro.it/opencoesione/docs/contesto/Indicatori_regionali_20130320.zip

dove `Indicatori_regionali_20130320.zip` risulta aggiornato il 20 marzo 2013.

Procedura di aggiornamento::

1. viene inoltrata una richiesta alla pagina del DPS
2. il risultato viene letto per verificare la data di aggiornamento degli Indicatori territoriali di contesto
3. controllo se la data è diversa da quella dell'ultimo aggiornamento fatto
4. viene scaricato l'archivio e opportunamente suddiviso (splitcsv3) nella cartella degli static files

3.a il file risulta già importato
    1. Esco dalla procedura

"""
import os
import re
import urllib2
import zipfile
from optparse import make_option
from django.conf import settings
from django.core.management import BaseCommand, CommandError
from open_coesione import utils

# web resource
DPS_URL = "http://www.dps.tesoro.it/opencoesione/dati_contesto.asp"
DPS_XPATH_PATTERN = "//table[@class='tab_100xcento_opencoesione']//td/a[@href]"
DPS_HREF_PATTERN = "/Indicatori_regionali_([\d]+)\.zip$"
DPS_ENCODING = 'ISO-8859-1'

# paths
DPS_ARCHIVE_PATH = settings.DPS_ISTAT_ROOT
DPS_LATEST_ARCHIVE_FILE = os.path.join(settings.DPS_ISTAT_ROOT, 'latest.zip')
DPS_STATIC_PATH = os.path.join(settings.DPS_ISTAT_ROOT, "static", "csv")
static = lambda *x: os.path.join(DPS_STATIC_PATH, *x)
DPS_REGIONS_CSV_FILE = 'regioni.csv'
DPS_REGIONS_CSV = static(DPS_REGIONS_CSV_FILE)
DPS_TOPIC_CSV_FILE = 'temi.csv'
DPS_TOPIC_CSV = static(DPS_TOPIC_CSV_FILE)
DPS_INDEXES_PATH = static('indicatori')
static_topic = lambda x: os.path.join(DPS_INDEXES_PATH, "{0}.csv".format(x))
DPS_TOPIC_INDEXES_PATH = static('temaind')
static_topic_index = lambda t, i: os.path.join(DPS_TOPIC_INDEXES_PATH, "{0}_{1}.csv".format(t, i))

REQUIRED_PATHS = [DPS_ARCHIVE_PATH, DPS_STATIC_PATH, DPS_INDEXES_PATH, DPS_TOPIC_INDEXES_PATH]

CURRENT = os.path.join(DPS_ARCHIVE_PATH, '.current')

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
        make_option('--url',
                    dest='url',
                    default=DPS_URL,
                    help='Url of source of istat-dps data'),
        make_option('--force-update',
                    dest='forceupdate',
                    default=False,
                    action='store_true',
                    help='Force extraction of archive'),
        make_option('--force-download',
                    dest='forcedownload',
                    default=False,
                    action='store_true',
                    help='Force download archive'),
        make_option('--force-all',
                    dest='forceall',
                    default=False,
                    action='store_true'),
        make_option('--nobackup',
                    dest='nobackup',
                    default=False,
                    action='store_true',
                    help='No backup required of latest csv files'),
        make_option('--collectstatic',
                    dest='collectstatic',
                    default=False,
                    action='store_true',
                    help='Collect static at the end of process'),

    )

    def handle(self, *args, **options):

        self.verbosity = int(options.get('verbosity', 1))

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

        DPS_URL = options.get('url')
        FORCE_UPDATE = options.get('forceupdate') or options.get('forceall')
        FORCE_DOWNLOAD = options.get('forcedownload') or options.get('forceall')

        try:

            archive_url, archive_file_name = self.scrape_archive_url(DPS_URL)

            archive_path = os.path.join(DPS_ARCHIVE_PATH, archive_file_name)
            archive_exists = os.path.isfile(archive_path)

            if archive_exists and not FORCE_UPDATE:
                self.stdout.write("Archive '{0}' has been already loaded. \n"
                                  "No updates availables. Use --force-update to reload\n".format(archive_path))
                return

            if not archive_exists or FORCE_DOWNLOAD:
                self.retrieve_archive_from_dps(archive_url, archive_path)

            csv_path = self.extract_archive(archive_path)

            if not options.get('nobackup') and os.path.isfile(CURRENT):
                self.backup_latest()

            self.load_csv(csv_path)

            # clean csv file
            os.remove(csv_path)

            with open(CURRENT, 'w') as current:
                # update .current file
                current.write(archive_path)

        except urllib2.HTTPError, e:
            raise CommandError("HTTP Error {1} '{0}'".format(e.code, e.url))
        except urllib2.URLError, e:
            raise CommandError("URL Error {1} '{0}'".format(e.reason, e))

        if options.get('collectstatic'):
            # if everything ok collect-static
            from django.core import management
            management.call_command('collectstatic', interactive=False, verbosity=self.verbosity)

    def scrape_archive_url(self, html_url):
        """
        Try to retrieve archive file url from html_url.
        :returns: archive_url to download and archive_file_name
        """
        from lxml import html
        # retrieve root element
        response = html.parse(html_url)
        # use xpath pattern to retrieve valid links
        valid_links = response.getroot().xpath(DPS_XPATH_PATTERN)
        # prepare pattern
        link_re = re.compile(DPS_HREF_PATTERN)
        # reduce valid_links
        valid_links = filter(lambda l: link_re.search(l.get('href')), valid_links)

        if len(valid_links) > 1:
            raise CommandError("Multiple valid links found "
                               "with xpath '{0}' in '{1}'".format(DPS_HREF_PATTERN, DPS_XPATH_PATTERN))
        elif len(valid_links) == 0:
            raise CommandError("Cannot find a link in '{0}' xpath "
                               "with '{1}' expression in href attribute".format(DPS_XPATH_PATTERN, DPS_HREF_PATTERN))
        archive_link = valid_links.pop()

        import urlparse
        archive_url = urlparse.urljoin(archive_link.base, archive_link.get('href'))
        archive_url = urlparse.urlparse(archive_url)
        if self.verbosity > 0:
            self.stdout.write("Detected archive from source: {0}\n".format(archive_url.geturl()))
        return archive_url.geturl(), archive_url.path.split('/')[-1]

    def retrieve_archive_from_dps(self, source_url, destination_path):
        """
        Try to retrieve zip archive from source_url
        and save it to destination_path.
        """
        try:
            if self.verbosity > 0:
                self.stdout.write("Update data from source: {0}\n".format(source_url))
            request = urllib2.Request(url=source_url)
            data = urllib2.urlopen(request)

            if self.verbosity > 1:
                self.stdout.write("Write archive to {0}\n".format(destination_path))
            with open(destination_path, "w") as output:
                # write zip content
                output.write(data.read())
        except IOError:
            raise CommandError("Cannot write file in {0}".format(destination_path))

    def extract_archive(self, archive_path, encoding=DPS_ENCODING):
        """Extract a zip archive file to csv with provided encoding.
        :returns: csv_path
        """
        if self.verbosity > 1:
            self.stdout.write("Extract archive: {0}\n".format(archive_path))

        zfile = zipfile.ZipFile(archive_path)
        # archive contains only one file
        csv_file_name = zfile.namelist().pop(0)
        csv_path = os.path.join(os.path.dirname(archive_path), csv_file_name)

        with open(csv_path, 'w') as extracted_csv:
            # write csv content
            extracted_csv.write(zfile.read(csv_file_name).decode(encoding).encode('utf8'))

        zfile.close()

        if self.verbosity > 0:
            self.stdout.write("Archive extracted in '{0}'\n".format(csv_path))

        return csv_path

    def load_csv(self, csv_path):
        """Load in memory parsed csv informations.
        Then execute write_files() and clean memory.
        """
        # prepare supporting data structures
        self.db = Storage()

        with open(csv_path) as csv_file:

            reader = utils.UnicodeDictReader(csv_file, delimiter=';')

            # check if is valid headers
            if reader.columns != CSV_COLUMNS:
                raise CommandError("Invalid columns format. The differences are: {0}".format(
                    set(CSV_COLUMNS).symmetric_difference(set(reader.columns))
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

        if self.verbosity > 0:
            self.stdout.write("Writing {0} regions\n".format(len(self.db.regions)))
        with open(DPS_REGIONS_CSV, 'wb') as csv_file:
            writer = utils.UnicodeDictWriter(csv_file, regions_fieldnames)
            writer.writeheader()

            for location_id in sorted(self.db.regions):
                writer.writerow_list([unicode(location_id), self.db.regions.get(location_id)])
            if self.verbosity > 1:
                self.stdout.write(u"{0}\n".format(u", ".join(self.db.regions.values())))

        if self.verbosity > 0:
            self.stdout.write('Writing {0} topics\n'.format(len(self.db.topics)))
        with open(DPS_TOPIC_CSV, 'wb') as csv_file:
            writer = utils.UnicodeDictWriter(csv_file, topic_columns)
            writer.writeheader()

            for topic_id in sorted(self.db.topics):
                writer.writerow_list([unicode(topic_id), self.db.topics.get(topic_id)])

        for topic_id in sorted(self.db.indexes_by_topic):
            if self.verbosity > 0:
                self.stdout.write(u"[{0}] {1}\n".format(topic_id, self.db.topics.get(topic_id)).encode('utf-8'))

            with open(static_topic(topic_id), 'wb') as csv_file:
                writer = utils.UnicodeDictWriter(csv_file, index_columns)
                writer.writeheader()

                for index_id in sorted(self.db.indexes_by_topic.get(topic_id)):
                    index = self.db.indexes[index_id]
                    if self.verbosity > 1:
                        self.stdout.write(
                            u"\n[{0}] [{1}] {2}\n    {3}".format(
                                topic_id, index_id, index.get('title'), index.get('subtitle')))
                    writer.writerow_list([unicode(index_id), index.get('title'), index.get('subtitle')])

                    with open(static_topic_index(topic_id, index_id), 'wb') as csv_index_file:
                        index_writer = utils.UnicodeDictWriter(csv_index_file, topic_index_columns)
                        index_writer.writeheader()

                        for location_id in sorted(self.db.values.get(index_id)):
                            values = [self.db.regions[location_id], ]
                            # collect values
                            for year in self.db.values.get(index_id).get(location_id):
                                val = self.db.values.get(index_id).get(location_id).get(year)
                                values.append(str(val) if val else '')
                                if self.verbosity > 1:
                                    self.stdout.write('.')

                            index_writer.writerow_list(values)
                if self.verbosity > 1:
                    self.stdout.write("\n")

    def backup_latest(self):
        """Execute a backup of current csv files and .current file.
        """
        if self.verbosity > 0:
            self.stdout.write("Backup of static/ directory to latest.zip\n")

        zip_file = None

        RELATIVE_PATH = static().replace(DPS_ARCHIVE_PATH, '')
        relative = lambda *x: os.path.join(RELATIVE_PATH, *x)
        try:
            zip_file = zipfile.ZipFile(DPS_LATEST_ARCHIVE_FILE, 'w', zipfile.ZIP_DEFLATED)
            # dump dowloaded archive
            zip_file.write(CURRENT, '/.current')
            # regioni.csv and temi.csv
            for file_name in [DPS_REGIONS_CSV_FILE, DPS_TOPIC_CSV_FILE]:
                zip_file.write(static(file_name), relative(file_name))
            # all subdirectories
            for folder in ['indicatori', 'temaind']:
                for root, folders, files in os.walk(static(folder)):
                    for file_name in files:
                        absolute_path = os.path.join(root, file_name)
                        zip_file.write(absolute_path, relative(folder, file_name))

        except IOError, message:
            raise CommandError(message)
        except OSError, message:
            raise CommandError(message)
        except zipfile.BadZipfile, message:
            raise CommandError(message)
        finally:
            if zip_file:
                zip_file.close()