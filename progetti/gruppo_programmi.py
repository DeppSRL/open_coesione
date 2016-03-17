# -*- coding: utf-8 -*-
from collections import OrderedDict
from django.db.models import Q
from django.utils.functional import cached_property
from progetti.models import ProgrammaAsseObiettivo, ProgrammaLineaAzione
from django.core.cache import cache


def split_by_type(programmi):
    programmi_splitted = {
        'programmi_asse_obiettivo': [],
        'programmi_linea_azione': []
    }
    for programma in programmi:
        if not programma.is_root:
            raise Exception('Only root programs allowed')
        elif programma.__class__.__name__ == 'ProgrammaAsseObiettivo':
            programmi_splitted['programmi_asse_obiettivo'].append(programma)
        elif programma.__class__.__name__ == 'ProgrammaLineaAzione':
            programmi_splitted['programmi_linea_azione'].append(programma)
        else:
            raise Exception('Wrong programma. Should not happen.')

    return programmi_splitted


class Config(object):
    @staticmethod
    def get_lista_programmi():
        programmi_asse_obiettivo = cache.get('programmi_asse_obiettivo')
        if programmi_asse_obiettivo is None:
            programmi_asse_obiettivo = ProgrammaAsseObiettivo.objects.programmi().order_by('descrizione')
            cache.set('programmi_asse_obiettivo', programmi_asse_obiettivo)

        programmi_linea_azione = cache.get('programmi_linea_azione')
        if programmi_linea_azione is None:
            programmi_linea_azione = ProgrammaLineaAzione.objects.programmi().order_by('descrizione')
            cache.set('programmi_linea_azione', programmi_linea_azione)

        programmi_pac_fsc = cache.get('programmi_pac_fsc')
        if programmi_pac_fsc is None:
            programmi_pac_fsc = programmi_linea_azione.filter(
                Q(descrizione__contains='DIRETTRICI FERROVIARIE') |
                Q(descrizione__contains='GIUSTIZIA CIVILE') |
                Q(descrizione__contains='(PNA) FSC DA EXPO AI TERRITORI') |
                Q(descrizione__contains='(PRA) FSC SARDEGNA')
            )
            cache.set('programmi_pac_fsc', programmi_pac_fsc)

        programmi_pac_fesr = cache.get('programmi_pac_fesr')
        if programmi_pac_fesr is None:
            programmi_pac_fesr = programmi_asse_obiettivo.filter(
                Q(descrizione__contains='FESR') & (
                    Q(descrizione__contains='ATTRATTORI CULTURALI') |
                    Q(descrizione__contains='RETI E MOBILITÀ') |
                    Q(descrizione__contains='CAMPANIA') |
                    Q(descrizione__contains='CALABRIA') |
                    Q(descrizione__contains='SICILIA') |
                    Q(descrizione__contains='SARDEGNA')
                )
            )
            cache.set('programmi_pac_fesr', programmi_pac_fesr)

        programmi_pac_fse = cache.get('programmi_pac_fse')
        if programmi_pac_fse is None:
            programmi_pac_fse = programmi_asse_obiettivo.filter(
                Q(descrizione__contains='CONV FSE') & (
                    Q(descrizione__contains='CAMPANIA') |
                    Q(descrizione__contains='CALABRIA') |
                    Q(descrizione__contains='SICILIA') |
                    Q(descrizione__contains='PUGLIA') |
                    Q(descrizione__contains='BASILICATA')
                )
            )
            cache.set('programmi_pac_fse', programmi_pac_fse)

        # some fsc lists must be built by hand
        # lista_programmi_fsc_pas = OrderedDict([
        #     (u'PROGRAMMA ATTUATIVO SPECIALE FSC COMUNE DI PALERMO', u'2007SI002FAPA1'),
        #     (u'PROGRAMMA ATTUATIVO SPECIALE FSC DIRETTRICI FERROVIARIE', u'2007IT001FA005'),
        #     (u'PROGRAMMA ATTUATIVO SPECIALE FSC GIUSTIZIA CIVILE CELERE PER LA CRESCITA', u'2007IT005FAMG1'),
        #     (u'PROGRAMMA ATTUATIVO SPECIALE FSC RI.MED', u'2007IT002FA030'),
        #     (u'PROGRAMMA STRATEGICO FSC COMPENSAZIONI AMBIENTALI REGIONE CAMPANIA', u'2007IT005FAMAC'),
        # ])
        # lista_programmi_fsc_pna = OrderedDict([
        #     (u'PROGRAMMA NAZIONALE DI ATTUAZIONE (PNA) FSC DA EXPO AI TERRITORI', u'2007IT001FA003'),
        #     (u"PROGRAMMA NAZIONALE DI ATTUAZIONE (PNA) FSC NUOVA IMPRENDITORIALITA' AGRICOLA", u'2007IT006FISMA'),
        #     (u'PROGRAMMA NAZIONALE DI ATTUAZIONE (PNA) FSC RISANAMENTO AMBIENTALE', u'2007IT004FAMA1'),
        # ])

        lista_programmi = {
            'fse': [p for p in programmi_asse_obiettivo if ' FSE ' in p.descrizione.upper()],
            'fesr': [p for p in programmi_asse_obiettivo if ' FESR ' in p.descrizione.upper()],
            'fsc': [
                OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith('PAR')]))),
                OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith(('PROGRAMMA ATTUATIVO', 'PROGRAMMA STRATEGICO'))]))),
                OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith('PROGRAMMA REGIONALE')]))),
                OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith('PROGRAMMA NAZIONALE')]))),
                OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith('PIANO STRAORDINARIO TUTELA E GESTIONE RISORSA IDRICA')]))),
                OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith('PROGRAMMA OBIETTIVI DI SERVIZIO')]))),
            ],
            'pac_pac_m': OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith('PROGRAMMA PAC') and (' MINISTERO ' in p.descrizione.upper() or ' PCM ' in p.descrizione.upper() or ' GOVERNANCE ' in p.descrizione.upper())]))),
            'pac_pac_r': OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith('PROGRAMMA PAC') and not (' MINISTERO ' in p.descrizione.upper() or ' PCM ' in p.descrizione.upper() or ' GOVERNANCE ' in p.descrizione.upper())]))),
            'pac_fsc': OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_pac_fsc]))),
            'pac_fesr': OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_pac_fesr]))),
            'pac_fse': OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_pac_fse]))),
        }

        return lista_programmi


class GruppoProgrammi(object):
    CODICI = ('ue-fesr', 'ue-fse', 'fsc', 'pac')

    codice = None

    def __init__(self, codice):
        if codice in self.CODICI:
            self.codice = codice
        else:
            raise ValueError('Wrong codice: {}'.format(codice))

    def __unicode__(self):
        return u'{}'.format(self.descrizione)

    @property
    def descrizione(self):
        return u'Programmi {}'.format(self.codice.replace('-', ' ').upper())

    @cached_property
    def programmi(self):
        programmi = None

        lista_programmi = Config.get_lista_programmi()

        if self.codice == 'ue-fesr' or self.codice == 'ue-fse':
            programmi = lista_programmi[self.codice.replace('ue-', '')]
        elif self.codice == 'fsc' or self.codice == 'pac':
            from itertools import chain

            if self.codice == 'fsc':
                ids = list(chain.from_iterable([x.values() for x in lista_programmi['fsc']]))
            else:
                ids = lista_programmi['pac_pac_m'].values() + lista_programmi['pac_pac_r'].values()

            programmi = list(chain(ProgrammaAsseObiettivo.objects.filter(pk__in=ids), ProgrammaLineaAzione.objects.filter(pk__in=ids)))

        return programmi

    @cached_property
    def dotazione_totale(self):
        dotazione_totale = 0
        for programma in self.programmi:
            if programma.dotazione_totale:
                dotazione_totale += programma.dotazione_totale

        return dotazione_totale
