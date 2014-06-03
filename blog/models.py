from datetime import datetime
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

    def __unicode__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None):
        if self.body and not self.body_plain:
            self.body_plain = strip_tags(self.body)
        if not self.published_at:
            self.published_at = datetime.now()
        return super(Entry, self).save(force_insert, force_update, using)

    class Meta:
        ordering= ['-published_at']
        verbose_name= 'articolo'
        verbose_name_plural= 'articoli'

class Blog(object):

    @staticmethod
    def get_latest_entries(qnt=10, end_date=None, start_date=None, single=False):
        end_date = end_date or datetime.now()
        qnt = qnt if not single else 1

        if start_date:
            entries = Entry.objects.filter(published_at__range=(start_date, end_date))[:qnt]
        else :
            entries = Entry.objects.filter(published_at__lte=end_date)[:qnt]

        if single :
            return entries[0] if entries else None

        return entries
