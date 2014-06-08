from django.conf import settings
from django.db.models import Q
from django.utils.datastructures import SortedDict
from blog.models import Blog
from progetti.models import ClassificazioneAzione, Tema, ProgrammaAsseObiettivo, ProgrammaLineaAzione
from territori.models import Territorio
from django.core.cache import cache


def main_settings(request):
    """
    this function adds a subset of application settings to template context
    """

    # Nella lista delle Nature 'Dati non disponibili' va per ultimo
    # cache
    classificazioni = cache.get('classificazioni')
    if classificazioni is None:
        classificazioni, non_disp = [], None
        for natura in ClassificazioneAzione.objects.tematiche():
            if natura.descrizione.strip() == '':
                non_disp = natura
            else:
                classificazioni.append(natura)
        classificazioni.append(non_disp)
        cache.set('classificazioni', classificazioni)

    # cache
    regioni = cache.get('territori.regioni')
    if regioni is None:
        regioni = Territorio.objects.filter(territorio=Territorio.TERRITORIO.R).defer('geom')
        cache.set('territori.regioni', regioni)

    # cache
    temi = cache.get('temi')
    if temi is None:
        temi = Tema.objects.principali()
        cache.set('temi', temi)

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
        programmi_pac_fse = ProgrammaAsseObiettivo.objects.filter(
            tipo_classificazione=ProgrammaAsseObiettivo.TIPO.programma
        ).filter(
            Q(descrizione__contains="CONV FSE") & (
                Q(descrizione__contains="CAMPANIA") |
                Q(descrizione__contains="CALABRIA") |
                Q(descrizione__contains="SICILIA") |
                Q(descrizione__contains="PUGLIA") |
                Q(descrizione__contains="BASILICATA")
            )
        )
        cache.set('programmi_pac_fse', programmi_pac_fse)


    programmi_pac_fesr = cache.get('programmi_pac_fesr')
    if programmi_pac_fesr is None:
        programmi_pac_fesr = ProgrammaAsseObiettivo.objects.filter(
            tipo_classificazione=ProgrammaAsseObiettivo.TIPO.programma
        ).filter(
            Q(descrizione__contains="CONV FESR") & (
                Q(descrizione__contains="CAMPANIA") |
                Q(descrizione__contains="CALABRIA") |
                Q(descrizione__contains="SICILIA")
            )
        )
        cache.set('programmi_pac_fesr', programmi_pac_fesr)

    programmi_pac_fsc = cache.get('programmi_pac_fsc')
    if programmi_pac_fsc is None:
        programmi_pac_fsc = ProgrammaAsseObiettivo.objects.filter(
            tipo_classificazione=ProgrammaAsseObiettivo.TIPO.programma
        ).filter(
            Q(descrizione__contains="GIUSTIZIA CIVILE") |
            Q(descrizione__contains="DIRETTRICI FERROVIARIE") |
            Q(descrizione__contains="(PRA) FSC SARDEGNA")
        )
        cache.set('programmi_pac_fsc', programmi_pac_fsc)

    return {
        'DEBUG': settings.DEBUG,
        'TEMPLATE_DEBUG': settings.TEMPLATE_DEBUG,
        'STATIC_URL': settings.STATIC_URL,
        'TILESTACHE_URL': settings.TILESTACHE_URL,
        'lista_regioni': regioni,
        'lista_tipologie_principali': classificazioni,
        'lista_temi_principali': temi,
        'latest_entry': Blog.get_latest_entries(single=True),
        'lista_programmi': {
            'fse': [p for p in programmi.order_by('descrizione') if ' FSE ' in p.descrizione.upper()],
            'fesr': [p for p in programmi.order_by('descrizione') if ' FESR ' in p.descrizione.upper()],
            'fsc_par': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea if "PAR " in p.descrizione]))),
            'fsc_pa': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea if "IT" in p.codice]))),
            'fsc_pra': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea if "(PRA)" in p.descrizione]))),
            'pac_pac': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_linea if "PAC " in p.descrizione]))),
            'pac_fse': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_pac_fse]))),
            'pac_fesr': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_pac_fesr]))),
            'pac_fsc': SortedDict(sorted(list([(p.descrizione, p.codice) for p in programmi_pac_fsc]))),
        },
    }
