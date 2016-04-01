# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from views import ShortURLRedirectView


urlpatterns = patterns(
    '',
    url(r'^(?P<code>\w+)$', ShortURLRedirectView.as_view(), name='urlshortener-shorturl'),
)
