# -*- coding: utf-8 -*-
from django.db import models
from model_utils import Choices
from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class Timestampable(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """
    created_at = AutoCreatedField('data di creazione')
    updated_at = AutoLastModifiedField('data di modifica')

    class Meta:
        abstract = True


class Contatto(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField('nome', max_length=100, blank=True, null=True)
    last_name = models.CharField('cognome', max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Contatto'
        verbose_name_plural = 'Contatti'

    def __unicode__(self):
        return self.email


class IscrizioneManager(models.Manager):
    @classmethod
    def add_iscrizione_complessa(cls, source_dict, contact_dict, iscrizione_dict):

        if source_dict:
            source, created = Fonte.objects.get_or_create(
                slug=source_dict['slug'],
                defaults=source_dict,
            )
        else:
            source = None

        contact, created = Contatto.objects.get_or_create(
            email=contact_dict['email'],
            defaults=contact_dict
        )

        i = Iscrizione(**iscrizione_dict)
        i.contact = contact
        i.source = source
        i.save()

        return i


class Iscrizione(Timestampable, models.Model):
    TYPES = Choices(
        ('cittadino', 'Cittadino'),
        ('sviluppatore', 'Sviluppatore'),
        ('publicservant', 'Funzionario PA'),
        ('giornalista', 'Giornalista'),
    )

    contact = models.ForeignKey('Contatto', verbose_name='contatto')
    source = models.ForeignKey('Fonte', verbose_name='fonte', blank=True, null=True)
    title = models.CharField('qualifica', max_length=100, blank=True, null=True)
    role = models.CharField('ruolo', max_length=100, blank=True, null=True)
    user_type = models.CharField('tipologia utente', max_length=16, choices=TYPES, blank=True, null=True)
    notes = models.TextField('note', blank=True, null=True)

    objects = IscrizioneManager()

    @property
    def pippo(self):
        return self.get_user_type_display()

    @property
    def email(self):
        return self.contact.email

    class Meta:
        verbose_name = 'Iscrizione'
        verbose_name_plural = 'Iscrizioni'

    def __unicode__(self):
        return u'{} a {} - {}'.format(self.contact, self.source, self.created_at)


class Fonte(models.Model):
    name = models.CharField('nome', max_length=512)
    slug = models.SlugField('slug', max_length=256)
    uri = models.URLField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Fonte'
        verbose_name_plural = 'Fonti'

    def __unicode__(self):
        return self.name
