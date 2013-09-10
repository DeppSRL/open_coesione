from django.conf import settings
from blog.models import Blog
from progetti.models import ClassificazioneAzione, Tema, ProgrammaAsseObiettivo
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
        },
    }
