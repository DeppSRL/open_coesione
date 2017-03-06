# -*- coding: utf-8 -*-
import locale
from optparse import make_option
from sys import stdout

import csvkit as csv
import logging
import re

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand

from progetti.models import Progetto


class Command(BaseCommand):
    """
    Data are imported from their CSV sources.
    """
    help = 'Import data from csv'

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csv_file',
                    default='dati/export_asoc_oc_urls.csv',
                    help='Select csv file path.'),
        make_option('--out',
                    dest='out',
                    default=stdout,
                    help='Select csv outpput file, defaults to stdout.'),
        make_option('--encoding',
                    dest='encoding',
                    default='utf-8',
                    help='Set character encoding of input file.'),
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

        csvfile = options['csv_file']
        encoding = options['encoding']

        csv_out = out = options['out']

        if type(out) == str:
            csv_out = open(out, 'wb')

        writer = csv.writer(csv_out, delimiter=';', quotechar='"', encoding=encoding)
        writer.writerow(['slug', 'url', 'attivo', 'tema', 'natura', 'cup',
                         'programma', 'classificazione_qsn', 'fondo_comunitario',
                         'fin_totale_pubblico', 'fin_totale_pubblico_netto', 'pagamento',
                         'stato_progetto','stato_finanziamenti'])

        locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

        with open(csvfile, 'rb') as cfile:
            reader = csv.reader(cfile, delimiter=',', quotechar='"')
            for r in reader:
                slug = None
                url = '-'
                output_r = r
                if not r:
                    continue

                url = r[0].strip()
                slug_search = re.search(
                    '^(http://){0,1}(www\.){0,1}opencoesione.gov.it/progetti/('
                    '.*?)/?$',
                    url, re.IGNORECASE
                )
                if slug_search:
                    slug = slug_search.group(3)

                if slug and '/' not in slug:
                    output_r = [slug, r[0]]

                try:
                    p = Progetto.fullobjects.get(slug=slug)
                    is_active = p.active_flag
                    tema = p.tema.tema_superiore.short_label
                    natura = p.classificazione_azione.classificazione_superiore\
                        .short_label
                    cup = p.cup
                    programma = ','.join([f.descrizione for f in p.fonti_fin])
                    class_qsn = p.classificazione_qsn.classificazione_superiore.classificazione_superiore.descrizione
                    fondo_com = p.get_fondo_comunitario_display()

                    fin_tot = locale.currency(p.fin_totale_pubblico).replace('Eu', u'€')
                    fin_tot_netto = locale.currency(p.fin_totale_pubblico_netto).replace('Eu', u'€')
                    pagamento = locale.currency(p.pagamento).replace('Eu', u'€')
                    stato_fin = p.get_stato_finanziario_display()
                    stato_prog = p.get_stato_progetto_display()

                    output_r.extend([is_active, tema, natura, cup, programma, class_qsn, fondo_com,
                                     fin_tot, fin_tot_netto, pagamento,
                                     stato_fin, stato_prog])
                except ObjectDoesNotExist:
                    pass

                self.logger.info(r[0])
                writer.writerow(output_r)
