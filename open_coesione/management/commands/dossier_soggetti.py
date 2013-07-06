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
                    default='100',
                    help='top limit'),
    )

    logger = logging.getLogger('console')
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

        ## get top value from options
        top = int(options['top'])

        csv_writer = utils.UnicodeWriter(sys.stdout, dialect=utils.excel_semicolon)

        ## which forma giuridica has more attuatori
        self.logger.info(u"---- Che forma giuridica ha più attuatori?")
        print(u"---- Che forma giuridica ha più attuatori?")
        # extract all forma_giuridicas related to attuatori
        fgs = FormaGiuridica.objects.filter(
            soggetto__ruolo__ruolo=Ruolo.RUOLO.attuatore
        ).distinct()
        # annotate manually each forma giuridica, counting the number of soggetti
        fgs_annotated = [(fg.denominazione, fg.soggetti.count()) for fg in fgs]
        # sort based on number of sogetti, reversed
        fgs_annotated.sort(key=lambda x: x[1], reverse=True)
        # print the top brasses
        csv_writer.writerow(
            ['Denominazione', 'Numero soggetti']
        )

        if top == 0:
            top = len(fgs_annotated)
        for fg in fgs_annotated[:top]:
            csv_writer.writerow([
                fg[0],
                "{0}".format(fg[1]),
            ])


        # fetch all soggetti that have attuatore Role
        attuatori = Soggetto.objects.filter(
            ruolo__ruolo=Ruolo.RUOLO.attuatore
        ).distinct()

        ## which attuatore has more projects assigned
        self.logger.info(u"---- Quali attuatori hanno più soggetti?")
        print(u"---- Quali attuatori hanno più soggetti?")
        attuatori_n_projects_annotated = [(s.denominazione, s.slug, s.ruoli.count()) for s in attuatori]
        attuatori_n_projects_annotated.sort(key=lambda x: x[2], reverse=True)
        # print the top brasses
        csv_writer.writerow(
            ['Denominazione', 'Slug', 'Numero progetti']
        )
        if top == 0:
            top = len(attuatori_n_projects_annotated)
        for att in attuatori_n_projects_annotated[:top]:
            csv_writer.writerow([
                att[0],
                att[1],
                "{0}".format(att[2]),
            ])


        ## which attuatore has more money assigned
        self.logger.info(u"---- Quali attuatori hanno più finanziamenti?")
        print(u"---- Quali attuatori hanno più finanziamenti?")
        attuatori_fin_annotated = [
            (s.denominazione, s.slug,
             sum(p.fin_totale_pubblico for p in s.progetti)) for s in attuatori
        ]
        attuatori_fin_annotated.sort(key=lambda x: x[2], reverse=True)
        # print the top brasses
        csv_writer.writerow(
            ['Denominazione', 'Slug', 'Finanziamento']
        )
        if top == 0:
            top = len(attuatori_fin_annotated)
        for att in attuatori_fin_annotated[:top]:
            csv_writer.writerow([
                att[0],
                att[1],
                "{0:.2f}".format(att[2]),
            ])

        ## which attuatore has projects in more different regions
        self.logger.info(u"---- Quali attuatori hanno progetti in regioni differenti?")
        print(u"---- Quali attuatori hanno progetti in regioni differenti?")
        attuatori_regioni_annotated = [
            (s.denominazione, s.slug, s.regioni) for s in attuatori
        ]
        attuatori_regioni_annotated.sort(key=lambda x: len(x[2]), reverse=True)
        # print the top brasses
        csv_writer.writerow(
            ['Denominazione', 'Slug', 'Num Regioni', 'Regioni']
        )
        if top == 0:
            top = len(attuatori_regioni_annotated)
        for att in attuatori_regioni_annotated[:top]:
            csv_writer.writerow([
                att[0],
                att[1],
                str(len(att[2])),
                ",".join(map(str,list(att[2]))),
            ])


