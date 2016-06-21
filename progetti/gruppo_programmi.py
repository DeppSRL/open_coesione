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
                    Q(descrizione__contains='SICUREZZA') |
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

        lista_programmi = {
            'fse': [p for p in programmi_asse_obiettivo if ' FSE ' in p.descrizione.upper()],
            'fesr': [p for p in programmi_asse_obiettivo if ' FESR ' in p.descrizione.upper()],
            'fsc_1': [OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith('PAR')])))],
            # 'fsc_2': [OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith('INTESA ISTITUZIONALE DI PROGRAMMA')])))],
            'fsc_3': [
                OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith(('PROGRAMMA ATTUATIVO', 'PROGRAMMA STRATEGICO'))]))),
                OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith('PROGRAMMA REGIONALE')]))),
                OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith('PROGRAMMA NAZIONALE')]))),
                OrderedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea_azione if p.descrizione.upper().startswith('PIANO STRAORDINARIO')]))),
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
    GRUPPI_PROGRAMMI = {
        'ue-fesr': u'Programmi UE FESR',
        'ue-fse': u'Programmi UE FSE',
        'fsc': u'Programmi FSC',
        'fsc-1': u'Programmi Attuativi Regionali',
        # 'fsc-2': u'Intese Istituzionali di Programma',
        'fsc-3': u'Altri Programmi FSC',
        'pac': u'Programmi PAC',
    }

    codice = None

    def __init__(self, codice):
        if codice in self.GRUPPI_PROGRAMMI:
            self.codice = codice
        else:
            raise ValueError('Wrong codice: {}'.format(codice))

    def __unicode__(self):
        return u'{}'.format(self.descrizione)

    @property
    def descrizione(self):
        return self.GRUPPI_PROGRAMMI[self.codice]

    @cached_property
    def programmi(self):
        lista_programmi = Config.get_lista_programmi()

        if self.codice in ('ue-fesr', 'ue-fse'):
            programmi = lista_programmi[self.codice.replace('ue-', '')]
        else:
            from itertools import chain

            if self.codice == 'fsc':
                # ids = list(chain.from_iterable([x.values() for x in lista_programmi['fsc_1'] + lista_programmi['fsc_2'] + lista_programmi['fsc_3']]))
                ids = list(chain.from_iterable([x.values() for x in lista_programmi['fsc_1'] + lista_programmi['fsc_3']]))
            elif self.codice.startswith('fsc-'):
                ids = list(chain.from_iterable([x.values() for x in lista_programmi[self.codice.replace('-', '_')]]))
            else:
                ids = lista_programmi['pac_pac_m'].values() + lista_programmi['pac_pac_r'].values()

            programmi = list(chain(ProgrammaAsseObiettivo.objects.filter(pk__in=ids), ProgrammaLineaAzione.objects.filter(pk__in=ids)))

        return programmi

    @cached_property
    def dotazione_totale(self):
        return sum(programma.dotazione_totale or 0 for programma in self.programmi)
