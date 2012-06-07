from django.conf import settings

def main_settings(request):
    """
    this function add to template context a subset of application settings
    """
    print request
    return {
        'DEBUG': settings.DEBUG,
        'STATIC_URL': settings.STATIC_URL,
    }
