import csv
import logging
from optparse import make_option
from dateutil.parser import parse
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand
from open_coesione import utils
from progetti.models import Progetto


class Command(BaseCommand):
    """
    All projects listed in the csv-file are **de-activated**,
    and the ``data_ultimo_rilascio`` field is populated.

    De-activation here means that the ``active_flag`` is set to False.
    """
    help = "Deactivate progetti, listd in csv files"

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csvfile',
                    default='./progetti_inattivi.csv',
                    help='Select csv file'),
        make_option('--limit',
                    dest='limit',
                    default=0,
                    help='Limit of records to import'),
        make_option('--offset',
                    dest='offset',
                    default=0,
                    help='Offset of records to import'),
        make_option('--dryrun',
                    dest='dryrun',
                    action='store_true',
                    help='Offset of records to import'),
    )

    logger = logging.getLogger('csvimport')

    def handle(self, *args, **options):
        self.csv_file = options['csvfile']

        f = None

        # read first csv file
        try:
            f = open(self.csv_file, 'r')
            self.unicode_reader = utils.UnicodeDictReader(f, delimiter=';', encoding='utf8')
        except IOError:
            self.logger.error("It was impossible to open file %s" % self.csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s" % (self.csv_file, e.message))


        offset = options['offset']
        limit = options['limit']
        dryrun = options['dryrun']

        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        n = 0
        for r in self.unicode_reader:
            c = self.unicode_reader.reader.line_num - 1
            if c < int(offset):
                continue

            if int(limit) and\
               (c - int(offset) > int(limit)):
                break

            try:
                p = Progetto.fullobjects.get(pk=r['COD_LOCALE_PROGETTO'])
            except ObjectDoesNotExist:
                self.logger.warning("%s - Progetto non trovato: %s, skipping" % (c, r['COD_LOCALE_PROGETTO']))
                continue

            self.logger.info(u"%s, Progetto disattivato: %s" % (c, p))
            if not dryrun:
                p.active_flag = False
                p.data_ultimo_rilascio = parse(r['DATA_ULTIMO_RILASCIO']).strftime('%Y-%m-%d')
                p.save()



