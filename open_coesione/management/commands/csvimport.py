# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from open_coesione import utils
from optparse import make_option
import csv
import csvkit
from progetti.models import *


class Command(BaseCommand):
    """
    Data are imported from their CSV sources.
    """
    help = "Import data from csv"

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csvfile',
                    default='./progetti.csv',
                    help='Select csv file'),
        make_option('--type',
                    dest='type',
                    default=None,
                    help='Type of import: prog|ponrec|pongat'),
        make_option('--limit',
                    dest='limit',
                    default=0,
                    help='Limit of records to import'),
        make_option('--offset',
                    dest='offset',
                    default=0,
                    help='Offset of records to import'),
        make_option('--delete',
                    dest='delete',
                    action='store_true',
                    help='Delete records, before importing new'),
        make_option('--encoding',
                    dest='encoding',
                    default='utf8',
                    help='set character encoding of input file')
    )

    csv_file = ''
    encoding = 'iso-8859-1'
    logger = logging.getLogger('csvimport')
    unicode_reader = None

    def handle(self, *args, **options):
        self.csv_file = options['csvfile']
        self.encoding = options['encoding']

        # read first csv file
        try:
            self.unicode_reader = csvkit.CSVKitDictReader(open(self.csv_file, 'r'), delimiter=';', encoding=self.encoding)
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

        if options['type'] == 'prog':
            self.handle_programs(*args, **options)
        elif options['type'] == 'ponrec':
            self.handle_desc_ponrec(*args, **options)
        elif options['type'] == 'pongat':
            self.handle_desc_pongat(*args, **options)
        else:
            self.logger.error("Wrong type %s. Select among prog, ponrec and pongat." % options['type'])
            exit(1)

    def handle_programs(self, *args, **options):
        """
        Parse a csv file and add dotazione_totale info to records into ProgrammaAsseObiettivo or ProgrammaLineaAzione models
        """
        self.logger.info("Inizio import da %s" % self.csv_file)

        ccodice = 'OC_CODICE_PROGRAMMA'
        cvalore = None
        for row in self.unicode_reader:
            if not cvalore:
                columns = sorted(row.keys(), reverse=True)

                for col in columns:
                    if col.strip().startswith('DOTAZIONE TOTALE PROGRAMMA POST PAC '):
                        cvalore = col
                        break

                if not (cvalore and (ccodice in columns)):
                    self.logger.error("CSV mancante delle informazioni necessarie.")
                    exit(1)

            codice = row[ccodice].strip()
            if codice:
                valore = Decimal(row[cvalore].strip().replace('.', ''))

                self.logger.info("%s --> %s" % (codice, valore))

                found = False
                for model in [ProgrammaAsseObiettivo, ProgrammaLineaAzione]:
                    try:
                        programma = model.objects.get(pk=codice)
                    except:
                        pass
                    else:
                        programma.dotazione_totale = valore
                        programma.save()
                        found = True

                if not found:
                    self.logger.warning("Programma non trovato: %s. Skip." % codice)

        self.logger.info('Fine')

    def handle_desc_ponrec(self, *args, **options):
        self.logger.info("Inizio import da %s" % self.csv_file)
        self.logger.info("Encoding: %s" % self.encoding)
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        # read csv file, changing the default field delimiter
        try:
            self.unicode_reader = utils.UnicodeDictReader(open(self.csv_file, 'r'), delimiter=',', encoding=self.encoding)
        except IOError:
            self.logger.error("It was impossible to open file %s" % self.csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s" % (self.csv_file, e.message))

        if options['delete']:
            self.logger.error("Could not revert descriptions updates.")
            exit(1)

        updates = 0
        already_ok = 0
        not_found = 0
        duplicate = 0
        c = 0
        for r in self.unicode_reader:
            c += 1
            if c < int(options['offset']):
                continue

            if int(options['limit']) and (c - int(options['offset']) > int(options['limit'])):
                break

            # trasformazione per avere il codice_progetto_locale
            codice_progetto_locale = "1MISE{0}".format(r['CodiceLocaleProgetto'].strip())
            try:
                progetto = Progetto.objects.get(pk=codice_progetto_locale)
                self.logger.debug("%s - Progetto: %s" % (c, progetto.pk))
            except ObjectDoesNotExist:
                self.logger.warning("%s - Progetto non trovato: %s, skip" % (c, r['CodiceLocaleProgetto']))
                not_found += 1
                continue
            except MultipleObjectsReturned:
                self.logger.warning(u"%s - Più progetti con Codice: %s, skip" % (c, r['CodiceLocaleProgetto']))
                duplicate += 1
                continue

            sintesi = r['Sintesi'].strip()

            if sintesi:
                self.logger.info(u"Aggiornamento descrizione per il progetto %s" % progetto)
                progetto.descrizione = sintesi
                progetto.descrizione_fonte_nome = 'Open Data PON REC'
                progetto.descrizione_fonte_url = 'http://www.ponrec.it/open-data'
                progetto.save()
                updates += 1
            else:
                self.logger.info(u"Sintesi vuota per il progetto %s" % progetto)
                already_ok += 1

        self.logger.info(
            "Fine: %s descrizioni aggiornate, %s sintesi da importare erano vuote, %s progetti non sono stati trovati tramite il codice progetto locale, %s progetti si riferiscono a un CUP non univoco" %
            (updates, already_ok, not_found, duplicate)
        )

    def handle_desc_pongat(self, *args, **options):
        """
        PONREG descriptions import, from
        http://www.dps.tesoro.it/documentazione/QSN/docs/PO/Elenco_Beneficiari_PON_GAT_dati_31_AGOSTO_2013.csv
        """
        self.logger.info("Inizio import da %s" % self.csv_file)
        self.logger.info("Encoding: %s" % self.encoding)
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        # read csv file, changing the default field delimiter
        try:
            self.unicode_reader = utils.UnicodeDictReader(open(self.csv_file, 'r'), delimiter=';', encoding=self.encoding)
        except IOError:
            self.logger.error("It was impossible to open file %s" % self.csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s" % (self.csv_file, e.message))

        if options['delete']:
            self.logger.error("Could not revert descriptions updates.")
            exit(1)

        updates = 0
        already_ok = 0
        not_found = 0
        duplicate = 0
        c = 0
        for r in self.unicode_reader:
            c += 1
            if c < int(options['offset']):
                continue

            if int(options['limit']) and (c - int(options['offset']) > int(options['limit'])):
                break

            cup = r['CUP'].strip()
            try:
                progetto = Progetto.objects.get(cup=cup)
                self.logger.debug("%s - Progetto: %s" % (c, progetto.pk))
            except ObjectDoesNotExist:
                self.logger.warning("%s - Progetto non trovato: %s, skip" % (c, cup))
                not_found += 1
                continue
            except MultipleObjectsReturned:
                self.logger.warning(u"%s - Più progetti con CUP: %s, skip" % (c, cup))
                duplicate += 1
                continue

            sintesi = r['Sintesi intervento'].strip()

            if sintesi:
                self.logger.info(u"Aggiornamento descrizione per il progetto %s" % progetto)
                progetto.descrizione = sintesi
                progetto.descrizione_fonte_nome = 'Open Data PON GAT'
                progetto.descrizione_fonte_url = 'http://www.agenziacoesione.gov.it/it/pongat/comunicazione/elenco_beneficiari/index.html'
                progetto.save()
                updates += 1
            else:
                self.logger.info(u"Sintesi vuota per il progetto %s" % progetto)
                already_ok += 1

        self.logger.info(
            "Fine: %s descrizioni aggiornate, %s sintesi da importare erano vuote, %s progetti non sono stati trovati tramite il CUP, %s progetti si riferiscono a un CUP non univoco" %
            (updates, already_ok, not_found, duplicate)
        )
