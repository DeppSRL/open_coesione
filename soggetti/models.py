# -*- coding: utf-8 -*-
from django.db import models
from model_utils import Choices

class Soggetto(models.Model):
    RUOLO = Choices(
        ('1', 'programmatore', 'Programmatore'),
        ('2', 'attuatore', 'Attuatore'),
        ('3', 'destinatario', 'Destinatario del finanziamento'),
        ('4', 'realizzatore', 'Realizzatore')
    )
    codice_fiscale = models.CharField(max_length=16, primary_key=True)
    denominazione = models.CharField(max_length=255)
    ruolo = models.CharField(max_length=1, choices=RUOLO)

    @property
    def progetti(self):
        return self.progetto_set.all()

    def __unicode__(self):
        return "%s" % (self.denominazione, )

    class Meta:
        verbose_name_plural = "Soggetti"
