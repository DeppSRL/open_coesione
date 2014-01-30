from django.db import models
from model_utils import Choices
from model_utils.fields import AutoCreatedField, AutoLastModifiedField
from django.utils.translation import ugettext_lazy as _

import logging
logger = logging.getLogger('mail_bin')

class Timestampable(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """
    created_at = AutoCreatedField(_('creation time'))
    updated_at = AutoLastModifiedField(_('last modification time'))

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


class Iscrizione(Timestampable, models.Model):
    TYPES = Choices(
        ('cittadino', 'Cittadino'),
        ('sviluppatore', 'Sviluppatore'),
        ('publicservant', 'Public Servant'),
        ('giornalista', 'Giornalista'),
    )

    contact = models.ForeignKey('Contatto', verbose_name='contatto')
    source = models.ForeignKey('Fonte', verbose_name='fonte')
    title = models.CharField('qualifica', max_length=100, blank=True, null=True)
    role = models.CharField('ruolo', max_length=100, blank=True, null=True)
    user_type = models.CharField('tipologia utente', max_length=16, choices=TYPES, blank=True, null=True)
    notes = models.TextField('note', blank=True, null=True)

    @property
    def email(self):
        return self.contact.email

    class Meta:
        verbose_name = 'Iscrizione'
        verbose_name_plural = 'Iscrizioni'

    def __unicode__(self):
        return u"{0} a {1} - {2}".format(self.contact, self.source, self.created_at)


class Fonte(models.Model):
    name = models.CharField('nome', max_length=512)
    slug = models.SlugField('slug', max_length=256)
    uri = models.URLField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Fonte'
        verbose_name_plural = 'Fonti'

    def __unicode__(self):
        return self.name