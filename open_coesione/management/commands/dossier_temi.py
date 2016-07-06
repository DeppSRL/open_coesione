# -*- coding: utf-8 -*-
import logging
import sys
from django.core.management.base import BaseCommand
from open_coesione import utils
from optparse import make_option
from progetti.models import Progetto, Tema
from territori.models import Territorio


class Command(BaseCommand):
    """
    Which regions get the money, for what topic?
    """
    help = 'Which regions get the money, for what topic?'

    option_list = BaseCommand.option_list + (
        make_option('--topic',
                    dest='topic',
                    help='topic slug'),
        make_option('--topic-list', action='store_true', dest='topiclist',
                    help="Print the list of all topics' slugs and exit"),
    )

    logger = logging.getLogger('csvimport')
    unicode_writer = None

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

        if options['topiclist']:
            topics = Tema.objects.principali()
            for t in topics:
                print u'{}'.format(t.slug)
        elif options['topic']:
            try:
                tema = Tema.objects.principali().get(slug=options['topic'])
            except Tema.DoesNotExist:
                raise Exception('Unknown topic {}'.format(options['topic']))
            else:
                progetti = Progetto.objects.con_tema(tema)
                costo = progetti.totale_costi()
                costo_procapite = round(costo / Territorio.objects.nazione().popolazione_totale)

                csv_writer = utils.UnicodeWriter(sys.stdout, dialect=utils.excel_semicolon)
                csv_writer.writerow(self.get_first_row())

                for regione in Territorio.objects.regioni():
                    costo_regione = progetti.nei_territori([regione]).totale_costi()
                    costo_procapite_regione = round(costo_regione / regione.popolazione_totale) if regione.popolazione_totale else 0
                    csv_writer.writerow([
                        regione.denominazione,
                        '{:.2f}'.format(costo_regione),
                        '{:.2f}'.format(costo_procapite_regione),
                        '{:.2f}'.format(costo_regione / costo * 100),
                    ])

                csv_writer.writerow([
                    'TOTALE',
                    '{:.2f}'.format(costo),
                    '{:.2f}'.format(costo_procapite),
                    '{:.2f}'.format(100),
                ])
        else:
            raise Exception('Please select a topic slug')

    @staticmethod
    def get_first_row():
        return ['Regione', 'Finanziamento totale', 'Finanziamento pro capite', 'Percentuale finanziamento su tema']
