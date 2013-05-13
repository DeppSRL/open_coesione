# -*- coding: utf-8 -*-

from optparse import make_option
from django.core.management.base import BaseCommand, LabelCommand, CommandError
from open_coesione import utils

import sys
import logging
import csv
import os

class Command(LabelCommand):
    """
    Task to extract data related to a sample of all projects.
    The sample of projects can be extracted thewourh:

    # head -n 1 progetti_20120630.csv > progetti_sample.csv
    # tail -n +2 progetti_20120630.csv | shuf -n 10000 | sort >> progetti_sample.csv

    """
    args = "<filename>"
    help = "Produces a csv file of rows related to projects' sample."
    label = 'filename'

    option_list = BaseCommand.option_list + (
        make_option('--sample',
                    dest='proj_sample_file',
                    default='progetti_sample.csv',
                    help='Select projects sample csv file'),
        make_option('--data-root',
                    dest='data_root',
                    default='dati/dataset_latest/',
                    help='Data root path, where csv files are to be found'),
        make_option('--type',
                    dest='type',
                    default='loc',
                    help='Type of related data: loc|rec|pay'),
        make_option('--encoding',
                    dest='encoding',
                    default='latin1',
                    help='set character encoding of input (and output) csv files')
        )

    proj_sample_file = ''
    sorted_csv_file = ''
    data_root = ''
    encoding = ''
    logger = logging.getLogger('csvimport')
    proj_reader = None

    csv.register_dialect('opencoesione', delimiter=';', quoting=csv.QUOTE_ALL)

    def handle(self, *labels, **options):

        if len(labels) is not 1:
            raise CommandError('Enter just one %s.' % self.label)

        self.data_root = options['data_root']
        self.sorted_csv_file = os.path.join(self.data_root, labels[0])
        self.proj_sample_file = os.path.join(self.data_root, options['proj_sample_file'])
        self.encoding = options['encoding']

        # open sample progetto csv reader
        try:
            self.proj_reader = utils.UnicodeDictReader(
                open(self.proj_sample_file, 'r'),
                dialect='opencoesione',
                encoding=self.encoding
            )
        except IOError:
            self.logger.error("It was impossible to open file %s" % self.proj_sample_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s" % (self.proj_sample_file, e.message))
            exit(1)

        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        if options['type'] == 'loc':
            # to produce the full, sorted localizzazioni file
            # head -n 1 localizzazioni_20120630.csv > localizzazioni_sorted.csv
            # tail -n +2 localizzazioni_20120630.csv | sort >> localizzazioni_sorted.csv
            headers = [
                "COD_LOCALE_PROGETTO",
                "COD_REGIONE","DEN_REGIONE",
                "COD_PROVINCIA","DEN_PROVINCIA",
                "COD_COMUNE","DEN_COMUNE",
                "INDIRIZZO_PROG","CAP_PROG",
                "DPS_TERRITORIO_PROG","DPS_FLAG_CAP_PROG"
            ]
        elif options['type'] == 'rec':
            # to produce the full, sorted soggetti file
            # head -n 1 soggetti_20120630.csv > soggetti_sorted.csv
            # tail -n +2 soggetti_20120630.csv | sort >> soggetti_sorted.csv
            headers = [
                "COD_LOCALE_PROGETTO",
                "SOGG_COD_RUOLO","SOGG_DESCR_RUOLO","SOGG_PROGR_RUOLO",
                "DPS_CODICE_FISCALE_SOGG","DPS_DENOMINAZIONE_SOGG",
                "COD_FORMA_GIURIDICA_SOGG","DESCR_FORMA_GIURIDICA_SOGG",
                "COD_COMUNE_SEDE_SOGG","INDIRIZZO_SOGG","CAP_SOGG",
                "DESCRIZIONE_ATECO_SOGG", "COD_ATECO_SOGG"
            ]
        elif options['type'] == 'pay':
            headers = [
                "COD_LOCALE_PROGETTO",
                "DATA_AGGIORNAMENTO",
                "TOT_PAGAMENTI"
            ]
        else:
            raise CommandError("Wrong type %s. Select between loc and rec." % options['type'])

        # open sorted csv file from where to extract record related to progetti_sample
        csv_file = os.path.join(self.data_root, labels[0])
        self.logger.info("Inizio ricerca in %s" % csv_file)

        try:
            reader = utils.UnicodeDictReader(
                open(csv_file, 'r'),
                dialect='opencoesione',
                encoding=self.encoding)
        except IOError:
            self.logger.error("It was impossible to open file %s" % csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s" % (csv_file, e.message))


        # loop over progetto_sample and advance in localizzazioni, to fetch related records
        # this is of O(n), and reduces drastically the extraction time
        writer = None
        for proj_row in self.proj_reader:
            proj_codice_locale = proj_row['COD_LOCALE_PROGETTO']

            loc = reader.next()
            if writer is None:
                writer = utils.UnicodeDictWriter(sys.stdout, headers, dialect='opencoesione', encoding=self.encoding)
            while loc['COD_LOCALE_PROGETTO'] < proj_codice_locale:
                loc = reader.next()
            writer.writerow(loc)

            loc = reader.next()
            while loc['COD_LOCALE_PROGETTO'] ==  proj_codice_locale:
                writer.writerow(loc)
                loc = reader.next()
