from django.db.models import Q
from django.utils.datastructures import SortedDict
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

class Config:
    @staticmethod
    def get_lista_programmi():
        # cache
        programmi = cache.get('programmi')
        if programmi is None:
            programmi = ProgrammaAsseObiettivo.objects.filter(tipo_classificazione=ProgrammaAsseObiettivo.TIPO.programma)
            cache.set('programmi', programmi)

        programmi_linea = cache.get('programmi_linea')
        if programmi_linea is None:
            programmi_linea = ProgrammaLineaAzione.objects.filter(tipo_classificazione=ProgrammaLineaAzione.TIPO.programma)
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
        lista_programmi_fsc_par = SortedDict(
            sorted(list([(p.descrizione, p.codice) for p in programmi_linea if 'PAR' == p.descrizione[:3]]))
        )
        lista_programmi_fsc_pa = SortedDict([
            (u'PROGRAMMA ATTUATIVO SPECIALE FSC DIRETTRICI FERROVIARIE', u'2007IT001FA005'),
            (u'PROGRAMMA ATTUATIVO SPECIALE FSC GIUSTIZIA CIVILE CELERE PER LA CRESCITA', u'2007IT005FAMG1'),
            (u'PROGRAMMA ATTUATIVO SPECIALE COMUNE DI PALERMO', u'2007SI002FAPA1'),
            (u'PROGRAMMA ATTUATIVO SPECIALE RI.MED', u'2007IT002FA030'),
            (u'PROGRAMMA STRATEGICO FSC COMPENSAZIONI AMBIENTALI REGIONE CAMPANIA', u'2007IT005FAMAC'),
        ])
        lista_programmi_fsc_pna = SortedDict([
            (u'PROGRAMMA NAZIONALE DI ATTUAZIONE (PNA) RISANAMENTO AMBIENTALE', u'2007IT004FAMA1')
        ])

        lista_programmi = {
            'fse': [p for p in programmi.order_by('descrizione') if ' FSE ' in p.descrizione.upper()],
            'fesr': [p for p in programmi.order_by('descrizione') if ' FESR ' in p.descrizione.upper()],
            'fsc_par': lista_programmi_fsc_par,
            'fsc_pa': lista_programmi_fsc_pa,
            'fsc_pra': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea if '(PRA)' in p.descrizione]))),
            'fsc_pna': lista_programmi_fsc_pna,
            'pac_pac': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea if 'PAC ' in p.descrizione]))),
            'pac_fse': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_pac_fse]))),
            'pac_fesr': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_pac_fesr]))),
            'pac_fsc': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_pac_fsc]))),
        }

        return lista_programmi

class GruppoProgrammi:
    CODICI = ['ue-fesr', 'ue-fse', 'fsc', 'pac']

    def __init__(self, codice):
        if codice in self.CODICI:
            self._codice = codice
            self._programmi = None
        else:
            raise ValueError('Wrong codice: %s' % codice)

    def programmi(self):
        if not self._programmi:
            lista_programmi = Config.get_lista_programmi()

            if self._codice == 'ue-fesr' or self._codice == 'ue-fse':
                self._programmi = lista_programmi[self._codice.replace('ue-', '')]
            elif self._codice == 'fsc' or self._codice == 'pac':
                if self._codice == 'fsc':
                    ids = lista_programmi['fsc_par'].values() + lista_programmi['fsc_pa'].values() + \
                          lista_programmi['fsc_pra'].values() + lista_programmi['fsc_pna'].values()
                else:
                    ids = lista_programmi['pac_pac'].values()

                from itertools import chain

                self._programmi = list(chain(ProgrammaAsseObiettivo.objects.filter(pk__in=ids), ProgrammaLineaAzione.objects.filter(pk__in=ids)))

        return self._programmi

    def codice(self):
        return self._codice

    def descrizione(self):
        return 'Programmi ' + self._codice.replace('-', ' ').upper()
