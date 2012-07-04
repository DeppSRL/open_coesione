# -*- coding: utf-8 -*-
from django.db import models
from model_utils import Choices


class FormaGiuridica(models.Model):
    codice = models.CharField(max_length=8, primary_key=True)
    denominazione = models.CharField(max_length=255)

    @property
    def soggetti(self):
        return self.soggetto_set.all()

    def __unicode__(self):
        return u"%s" % (self.denominazione,)

    class Meta:
        verbose_name = "Forma giuridica"
        verbose_name_plural = "Forme giuridiche"

class Soggetto(models.Model):
    RUOLO = Choices(
        ('1', 'programmatore', 'Programmatore'),
        ('2', 'attuatore', 'Attuatore'),
        ('3', 'destinatario', 'Destinatario del finanziamento'),
        ('4', 'realizzatore', 'Realizzatore')
    )
    codice_fiscale = models.CharField(max_length=16)
    denominazione = models.CharField(max_length=255)
    ruolo = models.CharField(max_length=1, choices=RUOLO)
    slug = models.CharField(max_length=300, blank=True, null=True)
    forma_giuridica = models.ForeignKey(FormaGiuridica,
                                        related_name='forma_giuridica_set',
                                        db_column='forma_giuridica')
    territorio = models.ForeignKey('territori.Territorio', null=True)
    rappresentante_legale = models.CharField(max_length=300, null=True, blank=True)
    indirizzo = models.CharField(max_length=300, null=True, blank=True)
    cap = models.CharField(max_length=5, null=True, blank=True)

    @property
    def progetti(self):
        return self.progetto_set.all()

    def __unicode__(self):
        return u"%s" % (self.denominazione, )

    @models.permalink
    def get_absolute_url(self):
        return ('soggetti_soggetto', (), {
            'slug': self.slug
        })

    class Meta:
        verbose_name_plural = "Soggetti"
