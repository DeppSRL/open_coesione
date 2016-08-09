# -*- coding: utf-8 -*-
from datetime import datetime
from django.conf import settings
# from django.contrib.sites.models import Site
from django.core.cache import cache
from blog.models import Entry
from progetti.gruppo_programmi import Config
from progetti.models import ClassificazioneAzione, Tema
from territori.models import Territorio


def main_settings(request):
    """
    this function adds a subset of application settings to template context
    """

    if any(path in request.path for path in ('/admin/', '/api/', '/leaflet/', '/mapnik/')):
        return {}
    else:
        regioni = cache.get('territori.regioni')
        if regioni is None:
            regioni = Territorio.objects.filter(territorio=Territorio.TERRITORIO.R).defer('geom')
            cache.set('territori.regioni', regioni)

        classificazioni = cache.get('classificazioni')
        if classificazioni is None:
            classificazioni = ClassificazioneAzione.objects.nature()
            cache.set('classificazioni', classificazioni)

        temi = cache.get('temi')
        if temi is None:
            temi = Tema.objects.principali()
            cache.set('temi', temi)

        # host = Site.objects.get(pk=settings.SITE_ID).domain
        host = request.META['HTTP_HOST']

        return {
            'DEBUG': settings.DEBUG,
            'TEMPLATE_DEBUG': settings.TEMPLATE_DEBUG,
            'USE_LESS': settings.USE_LESS,
            'STATIC_URL': settings.STATIC_URL,
            'SITE_URL': 'http://{}'.format(host),
            'IS_PRODUCTION': all(h not in host for h in ('localhost', 'staging')),
            'lista_regioni': regioni,
            'lista_classificazioni_principali': classificazioni,
            'lista_temi_principali': temi,
            'latest_entry': Entry.objects.filter(published_at__lte=datetime.now()).latest('published_at'),
            'lista_programmi': Config.get_lista_programmi(),
        }
