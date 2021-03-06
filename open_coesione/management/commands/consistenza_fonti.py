# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option
from progetti.models import *


class Command(BaseCommand):
    """
    Verifies and adjust consistency of the fonte_set for progetti.
    """
    help = "Verifies and adjust consistency of the fonte_set for the progetti"

    option_list = BaseCommand.option_list + (
        make_option('--data-path',
                    dest='data_path',
                    default='dati/dataset_dev',
                    help='The path where the data (csv) are stored. Relative to the project root.'),
        make_option('--fonte',
                    dest='fonte_codice',
                    default='FSC0713',
                    help='Select fonte code: FS0713 | FSC0713 | PAC'),
        make_option('--limit',
                    dest='limit',
                    default=0,
                    help='Limit of records to import'),
        make_option('--offset',
                    dest='offset',
                    default=0,
                    help='Offset of records to import'),
        make_option('--dry-run',
                    dest='dryrun',
                    action='store_true',
                    default=False,
                    help='Set the dry-run command mode: no actual modification is made'),
        )

    csv_file = ''
    logger = logging.getLogger('csvimport')
    unicode_reader = None

    def handle(self, *args, **options):
        data_path = options['data_path']
        fonte_codice = options['fonte_codice']
        fonte = Fonte.objects.get(codice=fonte_codice)
        csv_file = "{0}/clp_{1}.csv".format(data_path, fonte_codice)

        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        dryrun = options['dryrun']

        self.logger.info("Fonte: {0}".format(fonte_codice))

        # read the set of all clp from the file corresponding to the specified fonte
        self.logger.info("Reading CLP from csv file {0}".format(csv_file))
        with open(csv_file, 'rb') as f:
            set_csv = set(line[:-1] for line in f)

        # fetch the set of all clp for the given fonte
        self.logger.info("Fetching CLP from db".format(csv_file))
        set_db = set(Progetto.objects.filter(fonte_set__codice=fonte_codice, cipe_flag=False).values_list('codice_locale', flat=True))

        if dryrun:
            self.logger.info(u"Would remove {0} progetti: [{1}, ...]".format(
                len(set_db - set_csv), u",".join(list(set_db - set_csv)[:10])
            ))
            self.logger.info(u"Would add {0} progetti: [{1}, ...]".format(
                len(set_csv - set_db), u",".join(list(set_csv - set_db)[:10])
            ))
        else:
            for cod in set_db - set_csv:
                self.logger.info(u"Processing progetto {0}".format(cod))
                try:
                    p = Progetto.objects.get(codice_locale=cod)
                    fonte.progetto_set.remove(p)
                    self.logger.info("|-- Removed!")
                except ObjectDoesNotExist:
                    self.logger.debug("|-- Not found")

            for cod in set_csv - set_db:
                self.logger.info(u"Processing progetto {0}".format(cod))
                try:
                    p = Progetto.objects.get(codice_locale=cod)
                    fonte.progetto_set.add(p)
                    self.logger.info("|-- Added!")
                except ObjectDoesNotExist:
                    self.logger.debug("|-- Not found")







