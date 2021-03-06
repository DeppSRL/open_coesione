# -*- coding: utf-8 -*-
import os
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.flatpages.models import FlatPage
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from filebrowser.fields import FileBrowseField
from solo.models import SingletonModel
from tagging import models as tagging_models


FlatPage.add_to_class('extra_content', models.TextField('Contenuto sidebar', blank=True))


class BaseResource(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=255)
    content_object = generic.GenericForeignKey()

    description = models.CharField(max_length=255, verbose_name='Descrizione')
    large_description = models.CharField(max_length=512, verbose_name='Descrizione estesa', blank=True, null=True)
    priority = models.PositiveSmallIntegerField(default=0, verbose_name='Priorità')

    def __unicode__(self):
        return u'{}'.format(self.description)

    class Meta:
        abstract = True
        ordering = ['priority', 'description']


class File(BaseResource):
    file = models.FileField(max_length=255, upload_to=lambda instance, filename: 'files/{}/{}'.format(slugify('{} {}'.format(instance.content_type, instance.object_id)), filename))


class Link(BaseResource):
    url = models.URLField(max_length=255, verbose_name='URL')


class ContactMessage(models.Model):
    REASON_CHOICES = (
        (u'1', u'domanda sui dati'),
        (u'2', u'domanda sul sito'),
        (u'3', u'richiesta accesso API'),
        (u'4', u'esempio di riuso: applicazioni'),
        (u'5', u'esempio di riuso: visualizzazioni'),
        (u'6', u'esempio di riuso: analisi'),
        (u'7', u'segnalazione errore nei dati'),
        (u'8', u'segnalazione relativa a un progetto'),
        (u'9', u'suggerimenti e consigli'),
    )

    sender = models.CharField(max_length=50, verbose_name='Autore')
    email = models.EmailField()
    organization = models.CharField(max_length=100, verbose_name='Organizzazione')
    location = models.CharField(max_length=300, verbose_name='Luogo')
    reason = models.CharField(choices=REASON_CHOICES, max_length=1, verbose_name='Motivo del contatto')

    body = models.TextField(verbose_name='Messaggio')

    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Data di invio')

    class Meta:
        verbose_name = 'Messaggio'
        verbose_name_plural = 'Messaggi'


class PressReview(models.Model):
    title = models.CharField(max_length=200, verbose_name='Titolo')
    source = models.CharField(max_length=200, verbose_name='Fonte')
    author = models.CharField(max_length=200, verbose_name='Autore')
    file = models.FileField(upload_to='press', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    published_at = models.DateField(verbose_name='Data di pubblicazione')

    def __unicode__(self):
        return u'{}'.format(self.title)

    class Meta:
        verbose_name = 'Articolo'
        verbose_name_plural = 'Rassegna stampa'
        ordering = ['-published_at']


class Pillola(tagging_models.TagMixin, models.Model):
    title = models.CharField(max_length=200, verbose_name='Titolo')
    in_english = models.BooleanField(default=False, verbose_name='In inglese')
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    abstract = models.TextField(max_length=1024, verbose_name='Descrizione breve', blank=True, null=True)
    description = models.TextField(max_length=1024, verbose_name='Descrizione', blank=True, null=True)
    image = FileBrowseField(max_length=200, directory='immagini/', format='image', verbose_name='Immagine', blank=True, null=True)
    published_at = models.DateField(verbose_name='Data di pubblicazione')
    documents = generic.GenericRelation(File, verbose_name='Documenti')

    def get_absolute_url(self):
        return reverse('pillola', kwargs={'slug': self.slug})

    def __unicode__(self):
        return u'{}'.format(self.title)

    class Meta:
        verbose_name = 'Pillola'
        verbose_name_plural = 'Pillole'


class FAQ(models.Model):
    domanda_it = models.CharField(max_length=255, verbose_name='Domanda (italiano)')
    slug_it = models.SlugField(max_length=255, verbose_name='Slug (italiano)', unique=True)
    risposta_it = models.TextField(verbose_name='Risposta (italiano)', blank=True, null=True)
    domanda_en = models.CharField(max_length=255, verbose_name='Domanda (inglese)')
    slug_en = models.SlugField(max_length=255, verbose_name='Slug (inglese)', unique=True)
    risposta_en = models.TextField(verbose_name='Risposta (inglese)', blank=True, null=True)
    priorita = models.PositiveSmallIntegerField(default=0, verbose_name='Priorità')

    lang = 'it'

    def __getattr__(self, item):
        if item in ['domanda', 'risposta', 'slug'] and self.lang in ['it', 'en']:
            return getattr(self, item + '_' + self.lang)
        else:
            raise AttributeError('{!r} object has no attribute {!r}'.format(self.__class__.__name__, item))

    def __unicode__(self):
        return u'{}'.format(self.domanda)

    class Meta:
        verbose_name = 'Domanda frequente'
        verbose_name_plural = 'Domande frequenti'
        ordering = ['-priorita', 'id']


class Opportunita(SingletonModel):
    titolo = models.CharField(max_length=200)
    descrizione = models.TextField(max_length=1024, blank=True, null=True)
    file = models.FileField(u'File dati', max_length=255, upload_to='files')
    file2 = models.FileField(u'File metadati', max_length=255, upload_to='files')

    def __unicode__(self):
        return u'{}'.format(u'Opportunità')

    class Meta:
        verbose_name = u'opportunità'


@receiver(models.signals.post_delete, sender=File)
@receiver(models.signals.post_delete, sender=PressReview)
@receiver(models.signals.post_delete, sender=Opportunita)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem when corresponding sender object is deleted.
    """
    for attr in (f.name for f in sender._meta.fields if isinstance(f, models.FileField)):
        file = getattr(instance, attr, None)
        if file and os.path.isfile(file.path):
            os.remove(file.path)


@receiver(models.signals.pre_save, sender=File)
@receiver(models.signals.pre_save, sender=PressReview)
@receiver(models.signals.pre_save, sender=Opportunita)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes file from filesystem when corresponding sender object is changed.
    """
    if not instance.pk:
        return False

    for attr in (f.name for f in sender._meta.fields if isinstance(f, models.FileField)):
        try:
            old_file = getattr(sender.objects.get(pk=instance.pk), attr, None)
        except sender.DoesNotExist:
            continue

        if not hasattr(old_file, 'file'):
            continue

        new_file = getattr(instance, attr, None)
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
