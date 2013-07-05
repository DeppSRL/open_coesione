# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
import sys
from django.db.models import Count, Sum

from open_coesione import utils
from optparse import make_option
import logging

from progetti.models import Progetto, Tema, Ruolo
from soggetti.models import FormaGiuridica, Soggetto


class Command(BaseCommand):
    """
    Various fetches for soggetti:
    - which forma giuridica (association, company, public company ...) has more attuatori?
    - which attuatore has more money assigned?
    - which attuatore has more projects?
    - which attuatore has project in more different regions?
    """
    help = "Various fetches for soggetti."

    option_list = BaseCommand.option_list + (
        make_option('--top',
                    dest='top',
                    default='10',
                    help='top limit'),
    )

    logger = logging.getLogger('console')

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

        ## get top value from options
        top = int(options['top'])

        ## which forma giuridica has more attuatori
        top_fg = FormaGiuridica.objects.filter(
            soggetto__ruolo__ruolo=Ruolo.RUOLO.attuatore
        ).annotate(num_soggetti=Count('soggetto')).order_by('-num_soggetti')[:top]

        self.logger.info(u"---- Che forma giuridica ha più attuatori?")
        for fg in top_fg:
            self.logger.info("{0}: {1}".format(
                fg, fg.num_soggetti
            ))


        ## which attuatore has more projects assigned
        top_progetti = Soggetto.objects.filter(
            ruolo__ruolo=Ruolo.RUOLO.attuatore
        ).annotate(num_progetti=Count('ruolo')).order_by('-num_progetti')[:top]

        self.logger.info(u"---- Quali attuatori hanno più soggetti?")
        for att in top_progetti:
            self.logger.info("{0}: {1}".format(
                att, att.num_progetti
            ))


        ## which attuatore has more money assigned
        top_finanziamenti = Soggetto.objects.filter(
            ruolo__ruolo=Ruolo.RUOLO.attuatore
        ).annotate(fin=Sum('ruolo__progetto__fin_totale_pubblico')).order_by('-fin')[:top]

        self.logger.info(u"---- Quali attuatori hanno più finanziamenti?")
        for att in top_finanziamenti:
            self.logger.info("{0}: {1}".format(
                att, att.fin
            ))

        """
        attuatori_con_regione = Soggetto.objects.filter(
            ruolo__ruolo=Ruolo.RUOLO.attuatore
        ).values('slug', 'ruolo__progetto__territorio_set__cod_reg').distinct()
        for att in attuatori_con_regione:
        """


