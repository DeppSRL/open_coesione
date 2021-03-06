# -*- coding: utf-8 -*-
from datetime import datetime
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.html import strip_tags
from tagging import models as tagging_models


class Entry(tagging_models.TagMixin, models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    body = models.TextField()
    body_plain = models.TextField()
    published_at = models.DateTimeField(default=datetime.now(), verbose_name='Data di pubblicazione')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('blog_item', kwargs={'slug': self.slug})

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.body and not self.body_plain:
            self.body_plain = strip_tags(self.body)
        if not self.published_at:
            self.published_at = datetime.now()
        return super(Entry, self).save(force_insert, force_update, using)

    def __unicode__(self):
        return u'{0}'.format(self.title)

    class Meta:
        verbose_name = 'articolo'
        verbose_name_plural = 'articoli'
        ordering = ['-published_at']
