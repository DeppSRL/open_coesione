# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
import sys

from open_coesione import utils
from optparse import make_option
import logging

from progetti.models import Progetto, Tema
from territori.models import Territorio

class Command(BaseCommand):
    """
    Which regions get the money, for what topic?
    """
    help = "Which regions get the money, for what topic?"

    option_list = BaseCommand.option_list + (
        make_option('--topic',
                    dest='topic',
                    help='topic slug'),
        make_option('--topic-list', action='store_true', dest='topiclist',
                    help='Print the list of all topics\' slugs and exit'),
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

        ## handle request to show topics list
        if options['topiclist']:
            topics = Tema.objects.filter(tipo_tema=Tema.TIPO.sintetico)
            for t in topics:
                print u"{0}".format(t.slug)
            exit(1)

        csv_writer = utils.UnicodeWriter(sys.stdout, dialect=utils.excel_semicolon)
        csv_writer.writerow(self.get_first_row())


        ## fetch topic
        regs = Territorio.objects.regioni()
        if options['topic']:
            try:
                topic = Tema.objects.get(tipo_tema=Tema.TIPO.sintetico, slug=options['topic'])
            except ObjectDoesNotExist:
                raise Exception("Unknown topic {0}".format(options['topic']))
            costo = Progetto.objects.totale_costi(tema=topic)
            costo_procapite = Progetto.objects.totale_costi_procapite(tema=topic)
        else:
            raise Exception("Please select a topic slug")

        for reg in regs:
            costo_reg = Progetto.objects.totale_costi(tema=topic, territorio=reg)
            costo_procapite_reg = Progetto.objects.totale_costi_procapite(tema=topic, territorio=reg)
            csv_writer.writerow([
                reg.denominazione,
                "{0:.2f}".format(costo_reg),
                "{0:.2f}".format(costo_procapite_reg),
                "{0:.2f}".format(costo_reg/costo*100),
            ])

        csv_writer.writerow([
            "TOTALE",
            "{0:.2f}".format(costo),
            "{0:.2f}".format(costo_procapite),
            "{0:.2f}".format(100),
        ])

    def get_first_row(self):
        return ['Regione', 'Finanziamento totale', 'Finanziamento pro capite', 'Percentuale finanziamento su tema']





