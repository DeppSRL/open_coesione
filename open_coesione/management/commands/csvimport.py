# -*- coding: utf-8 -*-
import csv
import logging
from collections import defaultdict
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from open_coesione import utils
from optparse import make_option
from progetti.models import Progetto, ProgrammaAsseObiettivo, ProgrammaLineaAzione


class Command(BaseCommand):
    """
    Data are imported from their CSV sources.
    """
    help = 'Import data from csv'

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csvfile',
                    default='./progetti.csv',
                    help='Select csv file'),
        make_option('--type',
                    dest='type',
                    default=None,
                    help='Type of import: prog|ponrec|pongat'),
        make_option('--encoding',
                    dest='encoding',
                    default='utf8',
                    help='set character encoding of input file'),
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

        importtype = options['type']
        csv_file = options['csvfile']
        encoding = options['encoding']
        delimiter = ',' if importtype == 'ponrec' else ';'

        if not importtype in ('prog', 'ponrec', 'pongat'):
            self.logger.error(u'Wrong type {}. Select among prog, ponrec and pongat.'.format(importtype))
            exit(1)

        try:
            unicode_reader = utils.UnicodeDictReader(open(csv_file, 'r'), delimiter=delimiter, encoding=encoding)
        except IOError:
            self.logger.error(u'It was impossible to open file {}'.format(csv_file))
        except csv.Error, e:
            self.logger.error(u'CSV error while reading {}: {}'.format(csv_file, e.message))
        else:
            self.logger.info(u'Inizio import da {}'.format(csv_file))

            method = getattr(self, 'handle_{}'.format(importtype))
            method(unicode_reader)

            self.logger.info(u'Fine')

    def handle_prog(self, unicode_reader):
        ccodice = 'OC_CODICE_PROGRAMMA'
        cvalore = None

        for row in unicode_reader:
            if not cvalore:
                columns = sorted(row.keys(), reverse=True)

                for col in columns:
                    if col.strip().startswith('DOTAZIONE TOTALE PROGRAMMA POST PAC '):
                        cvalore = col
                        break

                if not (cvalore and (ccodice in columns)):
                    self.logger.error(u'CSV mancante delle informazioni necessarie.')
                    exit(1)

            codice = row[ccodice].strip()
            if codice:
                valore = Decimal(row[cvalore].strip().replace('.', ''))

                self.logger.info(u'{} --> {}'.format(codice, valore))

                found = False
                for model in (ProgrammaAsseObiettivo, ProgrammaLineaAzione):
                    try:
                        programma = model.objects.get(pk=codice)
                    except ObjectDoesNotExist:
                        pass
                    else:
                        programma.dotazione_totale = valore
                        programma.save()
                        found = True

                if not found:
                    self.logger.warning(u'Programma non trovato: {}. Skip.'.format(codice))

    def handle_ponrec(self, unicode_reader):
        report = defaultdict(int)

        for n, r in enumerate(unicode_reader, 1):
            codice = '1MISE{}'.format(r['CodiceLocaleProgetto'].strip())
            try:
                progetto = Progetto.objects.get(codice_locale=codice)
                self.logger.debug(u'{} - Progetto: {}'.format(n, progetto))
            except ObjectDoesNotExist:
                self.logger.warning(u'{} - Progetto non trovato: {}, skip'.format(n, codice))
                report['not_found'] += 1
                continue
            except MultipleObjectsReturned:
                self.logger.warning(u'{} - Più progetti con codice: {}, skip'.format(n, codice))
                report['duplicate'] += 1
                continue

            sintesi = r['Sintesi'].strip()

            if sintesi:
                self.logger.info(u'Aggiornamento descrizione per il progetto {}'.format(progetto))
                progetto.descrizione = sintesi
                progetto.descrizione_fonte_nome = 'Open Data PON REC'
                progetto.descrizione_fonte_url = 'http://www.ponrec.it/open-data'
                progetto.save()
                report['update'] += 1
            else:
                self.logger.info(u'Sintesi vuota per il progetto {}'.format(progetto))
                report['empty'] += 1

        self.logger.info(u'{update} descrizioni aggiornate, {empty} sintesi da importare erano vuote, {not_found} progetti non sono stati trovati, {duplicate} progetti si riferiscono a un codice non univoco'.format(**report))

    def handle_pongat(self, unicode_reader):
        report = defaultdict(int)

        for n, r in enumerate(unicode_reader, 1):
            codice = r['CUP'].strip()
            try:
                progetto = Progetto.objects.get(cup=codice)
                self.logger.debug(u'{} - Progetto: {}'.format(n, progetto))
            except ObjectDoesNotExist:
                self.logger.warning(u'{} - Progetto non trovato: {}, skip'.format(n, codice))
                report['not_found'] += 1
                continue
            except MultipleObjectsReturned:
                self.logger.warning(u'{} - Più progetti con codice: {}, skip'.format(n, codice))
                report['duplicate'] += 1
                continue

            sintesi = r['Sintesi intervento'].strip()

            if sintesi:
                self.logger.info(u'Aggiornamento descrizione per il progetto {}'.format(progetto))
                progetto.descrizione = sintesi
                progetto.descrizione_fonte_nome = 'Open Data PON GAT'
                progetto.descrizione_fonte_url = 'http://www.agenziacoesione.gov.it/it/pongat/comunicazione/elenco_beneficiari/index.html'
                progetto.save()
                report['update'] += 1
            else:
                self.logger.info(u'Sintesi vuota per il progetto {}'.format(progetto))
                report['empty'] += 1

        self.logger.info(u'{update} descrizioni aggiornate, {empty} sintesi da importare erano vuote, {not_found} progetti non sono stati trovati, {duplicate} progetti si riferiscono a un codice non univoco'.format(**report))
