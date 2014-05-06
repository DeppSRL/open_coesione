import csv
import logging
from optparse import make_option
from django.core.management import BaseCommand
from django.core.management.base import LabelCommand
from django.utils.text import slugify
from open_coesione import utils
from rubrica.models import IscrizioneManager


class Command(LabelCommand):
    """
    Contacts are imported from a CSV source

    Data are inserted by ``get_or_create``, so basically, import operations
    are isomorphic.
    """
    help = "Import contact data from csv"

    option_list = BaseCommand.option_list + (
        make_option('--source',
                    dest='source',
                    default='',
                    help='Name of the source. Optional.'),
        make_option('--source-uri',
                    dest='sourceuri',
                    default='',
                    help='URI of the source, if available.'),
        make_option('--limit',
                    dest='limit',
                    default=0,
                    help='Limit of records to import'),
        make_option('--offset',
                    dest='offset',
                    default=0,
                    help='Offset of records to import'),
        make_option('--encoding',
                    dest='encoding',
                    default='utf-8',
                    help='set character encoding of input file')
    )

    logger = logging.getLogger('csvimport')
    unicode_reader = None

    def handle_label(self, label, **options):
        self.csv_file = label
        self.source = options['source']
        self.sourceuri = options['sourceuri']
        self.limit = options['limit']
        self.offset = options['offset']
        self.encoding = options['encoding']


        # read csv file
        try:
            self.unicode_reader = utils.UnicodeDictReader(open(self.csv_file, 'r'), delimiter=';', encoding=self.encoding)
        except IOError:
            self.logger.error("It was impossible to open file %s" % self.csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s" % (self.csv_file, e.message))


        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        self.logger.info("Inizio import da %s" % self.csv_file)
        self.logger.info("Encoding: %s" % self.encoding)
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        c = 0
        for row in self.unicode_reader:
            # select a set of rows
            # with offset
            c += 1
            if c < int(options['offset']):
                continue
                # and limit
            if int(options['limit']) and\
               (c - int(options['offset']) > int(options['limit'])):
                break
            # ... i'm working...
            if c % 2500 == 0: self.logger.info( ".. read line %d .." % c )

            if self.source:
                source_dict = {
                    'name': self.source,
                    'slug': slugify(unicode(self.source)),
                    'uri': self.sourceuri
                }
            else:
                source_dict = None

            contact_dict = {
                'email': row['Email'].strip(),
                'first_name': row['Nome'].strip(),
                'last_name': row['Cognome'].strip()
            }
            iscrizione_dict = {
                'title': row['Qualifica'].strip(),
                'role': row['Ruolo'].strip(),
                'user_type': row['Tipo utente'].strip(),
                'notes': row['Note'].strip()
            }

            i = IscrizioneManager.add_iscrizione_complessa(
                source_dict, contact_dict, iscrizione_dict,
            )

            self.logger.debug(u"%s: processing: %s" % (c, i.email))


