from django.conf import settings
from blog.models import Blog
from progetti.models import ClassificazioneAzione, Tema
from territori.models import Territorio

def main_settings(request):
    """
    this function add to template context a subset of application settings
    """

    # Dati non disponibili per ultimo
    nature, non_disp = [], None
    for natura in ClassificazioneAzione.objects.tematiche():
        if natura.descrizione.strip() == '':
            non_disp = natura
        else :
            nature.append(natura)
    nature.append(non_disp)

    return {
        'DEBUG': settings.DEBUG,
        'TEMPLATE_DEBUG': settings.TEMPLATE_DEBUG,
        'STATIC_URL': settings.STATIC_URL,
        'TILESTACHE_URL': settings.TILESTACHE_URL,
        'lista_regioni': Territorio.objects.filter(territorio= Territorio.TERRITORIO.R),
        'lista_tipologie_principali': nature,
        'lista_temi_principali': Tema.objects.principali(),
        'latest_entry': Blog.get_latest_entries(single=True)
    }
