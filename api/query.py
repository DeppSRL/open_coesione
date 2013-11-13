from urllib import urlencode
from django.conf import settings
import requests


__author__ = 'daniele'


API_URL = getattr(settings, 'API_URL')


def request(query, **params):

    url = "{0}{1}".format(API_URL, query)
    if len(params):
        url += '?{0}'.format(urlencode(params))

    print url

    response = requests.get(url)

    return response.json()