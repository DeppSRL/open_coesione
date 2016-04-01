# -*- coding: utf-8 -*-
from base_62_converter import dehydrate, saturate
from django.core.urlresolvers import reverse
from django.db import models


class URLManager(models.Manager):
    def get(self, *args, **kwargs):
        if 'code' in kwargs:
            kwargs['pk'] = saturate(kwargs.pop('code'))

        return self.get_query_set().get(*args, **kwargs)


class URL(models.Model):
    url = models.URLField(max_length=255, verbose_name='URL')
    visit_count = models.PositiveIntegerField(default=0, verbose_name='Numero di visite')

    objects = URLManager()

    @property
    def code(self):
        return dehydrate(self.pk)

    def get_absolute_url(self):
        return reverse('urlshortener-shorturl', kwargs={'code': self.code})

    def __unicode__(self):
        return u'{}'.format(self.url)
