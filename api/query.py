from urllib import urlencode
from django.conf import settings
import requests


__author__ = 'daniele'


def request(query, **params):

    if request.API_URL is None:
        from django.contrib.sites.models import Site
        from django.core.urlresolvers import reverse
        request.API_URL = "http://{0}{1}".format(
            Site.objects.get_current().domain.rstrip('/'),
            reverse('api-root')
        )

    url = "{0}{1}".format(request.API_URL, query)
    if len(params):
        url += '?{0}'.format(urlencode(params))

    print url

    response = requests.get(url)

    return response.json()
request.API_URL = getattr(settings, 'API_URL', None)