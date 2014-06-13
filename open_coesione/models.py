# coding=utf-8
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.dispatch import receiver
import os
from tagging import models as tagging_models


class ContactMessage(models.Model):

    REASON_CHOICES = (
        (1, u'domanda sui dati'),
        (2, u'domanda sul sito'),
        (9, u'richiesta accesso API'),
        (3, u'esempio di riuso: applicazioni'),
        (4, u'esempio di riuso: visualizzazioni'),
        (5, u'esempio di riuso: analisi'),
        (6, u'segnalazione errore nei dati'),
        (7, u'segnalazione relativa a un progetto'),
        (8, u'suggerimenti e consigli'),
    )

    sender = models.CharField(max_length= 50, verbose_name='Autore')
    email = models.EmailField()
    organization = models.CharField(max_length= 100, verbose_name='Organizzazione')
    location = models.CharField(max_length=300, verbose_name='Luogo')
    reason = models.CharField(choices=REASON_CHOICES, max_length=1, verbose_name='Motivo del contatto')

    body = models.TextField( verbose_name='Messaggio' )

    sent_at = models.DateTimeField( auto_now_add=True, verbose_name="Data di invio" )

    class Meta:
        verbose_name_plural = "Messaggi"
        verbose_name = "Messaggio"

class PressReview(models.Model):

    title = models.CharField(max_length=200, verbose_name='Titolo')
    source = models.CharField(max_length=200, verbose_name='Fonte')
    author = models.CharField(max_length=200, verbose_name='Autore')

    file = models.FileField(upload_to='press', blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    published_at = models.DateField(verbose_name='Data di pubblicazione')

    class Meta:
        verbose_name_plural = "Rassegna stampa"
        verbose_name = "Articolo"


class Pillola(tagging_models.TagMixin, models.Model):

    title = models.CharField(max_length=200, verbose_name='Titolo')
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    abstract = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=1024, verbose_name='Descrizione', blank=True, null=True)
    file = models.FileField(upload_to='pillole', blank=True, null=True)
    published_at = models.DateField(verbose_name='Data di pubblicazione')

    class Meta:
        verbose_name_plural = "pillole"
        verbose_name = "pillola"


class URL(models.Model):
    url = models.URLField(max_length=255, blank=False, null=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=255)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = 'link'
        verbose_name_plural = 'links'


class FAQ(models.Model):

    domanda_it = models.CharField(max_length=255, verbose_name='Domanda (italiano)')
    slug_it = models.SlugField(max_length=255, verbose_name='Slug (italiano)', unique=True)
    risposta_it = models.TextField(verbose_name='Risposta (italiano)', blank=True, null=True)
    domanda_en = models.CharField(max_length=255, verbose_name='Domanda (inglese)')
    slug_en = models.SlugField(max_length=255, verbose_name='Slug (inglese)', unique=True)
    risposta_en = models.TextField(verbose_name='Risposta (inglese)', blank=True, null=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'domanda frequente'
        verbose_name_plural = 'domande frequenti'


# These two auto-delete files from filesystem when they are unneeded:
@receiver(models.signals.post_delete, sender=Pillola)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

@receiver(models.signals.pre_save, sender=Pillola)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `Pillola` object is changed.
    """
    if not instance.pk:
        return False

    try:
        old_file = Pillola.objects.get(pk=instance.pk).file
    except Pillola.DoesNotExist:
        return False

    if not hasattr(old_file, 'file'):
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
