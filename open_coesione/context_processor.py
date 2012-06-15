from django.conf import settings
from territori.models import Territorio

def main_settings(request):
    """
    this function add to template context a subset of application settings
    """

    return {
        'DEBUG': settings.DEBUG,
        'STATIC_URL': settings.STATIC_URL,

        'lista_regioni': Territorio.objects.filter(territorio= Territorio.TERRITORIO.R),
    }
