# -*- coding: utf-8 -*-
import logging
import sys
from django.core.management.base import BaseCommand
from open_coesione import utils
from optparse import make_option
from progetti.models import Progetto
from territori.models import Territorio


class Command(BaseCommand):
    """
    Which provinces get the money, subdivided by regions?
    """
    help = 'Which provinces get the money, subdivided by regions?'

    option_list = BaseCommand.option_list + (
        make_option('--region',
                    dest='region',
                    help='Region name, or nothing to get all provinces'),
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

        csv_writer = utils.UnicodeWriter(sys.stdout, dialect=utils.excel_semicolon)
        csv_writer.writerow(self.get_first_row())

        provincie = Territorio.objects.provincie()
        progetti = Progetto.objects

        if options['region']:
            try:
                territorio = Territorio.objects.regioni().get(denominazione__icontains=options['region'])
            except Territorio.DoesNotExist:
                raise Exception('Unknown region {}'.format(options['region']))
            else:
                provincie = provincie.filter(cod_reg=territorio.cod_reg)
                progetti = progetti.nei_territori([territorio])
        else:
            territorio = Territorio.objects.nazione()

        costo = progetti.totale_costi()
        costo_procapite = round(costo / territorio.popolazione_totale) if territorio.popolazione_totale else 0

        for provincia in provincie:
            costo_provincia = Progetto.objects.nei_territori([provincia]).totale_costi()
            costo_procapite_provincia = round(costo_provincia / provincia.popolazione_totale) if provincia.popolazione_totale else 0
            csv_writer.writerow([
                provincia.denominazione,
                '{:.2f}'.format(costo_provincia),
                '{:.2f}'.format(costo_procapite_provincia),
                '{:.2f}'.format(costo_provincia / costo * 100),
            ])

        csv_writer.writerow([
            'TOTALE',
            '{:.2f}'.format(costo),
            '{:.2f}'.format(costo_procapite),
            '{:.2f}'.format(100),
        ])

    @staticmethod
    def get_first_row():
        return ['Provincia', 'Finanziamento totale', 'Finanziamento pro capite', 'Percentuale finanziamento regionale']
