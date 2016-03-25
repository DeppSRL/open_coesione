# -*- coding: utf-8 -*-
from urllib import urlencode
from django.conf import settings
import requests

__author__ = 'daniele'


def request(query, **params):
    if request.api_url is None:
        from django.contrib.sites.models import Site
        from django.core.urlresolvers import reverse
        request.api_url = 'http://{}{}'.format(Site.objects.get_current().domain.rstrip('/'), reverse('api-root'))

    url = '{}{}'.format(request.api_url, query)
    if len(params):
        url += '?{}'.format(urlencode(params))

    print url

    response = requests.get(url)

    return response.json()

request.api_url = getattr(settings, 'API_URL', None)
