# -*- coding: utf-8 -*-
from django.db.models import Q
from django.utils.datastructures import SortedDict
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
        # cache
        programmi = cache.get('programmi')
        if programmi is None:
            programmi = ProgrammaAsseObiettivo.objects.programmi().order_by('descrizione')
            cache.set('programmi', programmi)

        programmi_linea = cache.get('programmi_linea')
        if programmi_linea is None:
            programmi_linea = ProgrammaLineaAzione.objects.programmi().order_by('descrizione')
            cache.set('programmi_linea', programmi_linea)

        programmi_pac_fse = cache.get('programmi_pac_fse')
        if programmi_pac_fse is None:
            programmi_pac_fse = programmi.filter(
                Q(descrizione__contains='CONV FSE') & (
                    Q(descrizione__contains='CAMPANIA') |
                    Q(descrizione__contains='CALABRIA') |
                    Q(descrizione__contains='SICILIA') |
                    Q(descrizione__contains='PUGLIA') |
                    Q(descrizione__contains='BASILICATA')
                )
            )
            cache.set('programmi_pac_fse', programmi_pac_fse)

        programmi_pac_fesr = cache.get('programmi_pac_fesr')
        if programmi_pac_fesr is None:
            programmi_pac_fesr = ProgrammaAsseObiettivo.objects.filter(
                tipo_classificazione=ProgrammaAsseObiettivo.TIPO.programma
            ).filter(
                Q(descrizione__contains="POIN CONV FESR ATTRATTORI CULTURALI") |
                Q(descrizione__contains="CONV FESR") & (
                    Q(descrizione__contains="CAMPANIA") |
                    Q(descrizione__contains="CALABRIA") |
                    Q(descrizione__contains="SICILIA")
                )
            )
            cache.set('programmi_pac_fesr', programmi_pac_fesr)

        programmi_pac_fsc = cache.get('programmi_pac_fsc')
        if programmi_pac_fsc is None:
            programmi_pac_fsc = programmi_linea.filter(
                Q(descrizione__contains='GIUSTIZIA CIVILE') |
                Q(descrizione__contains='DIRETTRICI FERROVIARIE') |
                Q(descrizione__contains='(PRA) FSC SARDEGNA')
            )
            cache.set('programmi_pac_fsc', programmi_pac_fsc)

        # some fsc lists must be built by hand
        lista_programmi_fsc_pa = SortedDict([
            (u'PROGRAMMA ATTUATIVO SPECIALE FSC DIRETTRICI FERROVIARIE', u'2007IT001FA005'),
            (u'PROGRAMMA ATTUATIVO SPECIALE FSC GIUSTIZIA CIVILE CELERE PER LA CRESCITA', u'2007IT005FAMG1'),
            (u'PROGRAMMA ATTUATIVO SPECIALE COMUNE DI PALERMO', u'2007SI002FAPA1'),
            (u'PROGRAMMA ATTUATIVO SPECIALE RI.MED', u'2007IT002FA030'),
            (u'PROGRAMMA STRATEGICO FSC COMPENSAZIONI AMBIENTALI REGIONE CAMPANIA', u'2007IT005FAMAC'),
        ])
        lista_programmi_fsc_pna = SortedDict([
            (u'PROGRAMMA NAZIONALE DI ATTUAZIONE (PNA) RISANAMENTO AMBIENTALE', u'2007IT004FAMA1'),
            (u"PROGRAMMA NAZIONALE DI ATTUAZIONE (PNA) FSC NUOVA IMPRENDITORIALITA' AGRICOLA", u'2007IT006FISMA'),
        ])

        lista_programmi = {
            'fse': [p for p in programmi if ' FSE ' in p.descrizione.upper()],
            'fesr': [p for p in programmi if ' FESR ' in p.descrizione.upper()],
            'fsc_par': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea if 'PAR' == p.descrizione.upper()[:3]]))),
            'fsc_pa': lista_programmi_fsc_pa,
            'fsc_pra': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea if '(PRA)' in p.descrizione.upper()]))),
            'fsc_pna': lista_programmi_fsc_pna,
            'fsc_pstg': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea if 'PIANO STRAORDINARIO TUTELA E GESTIONE RISORSA IDRICA' in p.descrizione.upper()]))),
            'pac_pac_m': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea if ' PAC ' in p.descrizione.upper() and (' MINISTERO ' in p.descrizione.upper() or ' PCM ' in p.descrizione.upper())]))),
            'pac_pac_r': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea if ' PAC ' in p.descrizione.upper() and not (' MINISTERO ' in p.descrizione.upper() or ' PCM ' in p.descrizione.upper())]))),
            'pac_fse': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_pac_fse]))),
            'pac_fesr': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_pac_fesr]))),
            'pac_fsc': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_pac_fsc]))),
        }

        return lista_programmi


class GruppoProgrammi(object):
    CODICI = ('ue-fesr', 'ue-fse', 'fsc', 'pac')

    codice = None

    def __init__(self, codice):
        if codice in self.CODICI:
            self.codice = codice
        else:
            raise ValueError('Wrong codice: {0}'.format(codice))

    def __unicode__(self):
        return u'{0}'.format(self.descrizione)

    @cached_property
    def programmi(self):
        programmi = None

        lista_programmi = Config.get_lista_programmi()

        if self.codice == 'ue-fesr' or self.codice == 'ue-fse':
            programmi = lista_programmi[self.codice.replace('ue-', '')]
        elif self.codice == 'fsc' or self.codice == 'pac':
            if self.codice == 'fsc':
                ids = lista_programmi['fsc_par'].values() + lista_programmi['fsc_pa'].values() + \
                      lista_programmi['fsc_pra'].values() + lista_programmi['fsc_pna'].values() + \
                      lista_programmi['fsc_pstg'].values()
            else:
                ids = lista_programmi['pac_pac_m'].values() + lista_programmi['pac_pac_r'].values()

            from itertools import chain

            programmi = list(chain(ProgrammaAsseObiettivo.objects.filter(pk__in=ids), ProgrammaLineaAzione.objects.filter(pk__in=ids)))

        return programmi

    @property
    def descrizione(self):
        return u'Programmi {0}'.format(self.codice.replace('-', ' ').upper())
