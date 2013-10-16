from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse_lazy
from django.utils.http import urlencode
import requests


__author__ = 'daniele'


API_URL = getattr(settings, 'API_URL')
if API_URL is None:
    API_URL = "http://{0}{1}".format(
        Site.objects.get_current().domain,
        reverse_lazy('api-root')
    )


def request(query, **params):

    url = "{0}{1}".format(API_URL, query)
    if len(params):
        url += '?{0}'.format(urlencode(params))

    print url

    response = requests.get(url)

    return response.json()
