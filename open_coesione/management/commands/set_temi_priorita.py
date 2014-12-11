# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from progetti.models import Tema


class Command(BaseCommand):
    def handle(self, *args, **options):
        ordered = [
            u'Ricerca e innovazione',
            u'Agenda digitale',
            u'Competitività imprese',
            u'Energia',
            u'Ambiente',
            u'Cultura e turismo',
            u'Trasporti',
            u'Occupazione',
            u'Inclusione sociale',
            u'Infanzia e anziani',
            u'Istruzione',
            u'Città e aree rurali',
            u'Rafforzamento PA',
        ]
        for tema in Tema.objects.principali():
            try:
                tema.priorita = ordered.index(tema.short_label) + 1
                tema.save()
            except:
                print(u'ERRORE: {0} ({1})'.format(tema.descrizione, tema.short_label))
            else:
                print(u'OK: {0} ({1}): {2}'.format(tema.descrizione, tema.short_label, tema.priorita))
