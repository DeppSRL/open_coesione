# -*- coding: utf-8 -*-

from django.contrib.gis.db import models
from model_utils import Choices

class Localita(models.Model):
    TERRITORIO = Choices(
        ('C', 'Comune'),
        ('P', 'Provincia'),
        ('R', 'Regione'),
        ('N', 'Nazionale'),
        ('E', 'Estero'),
    )
    cod_reg = models.IntegerField(default=0, blank=True, null=True)
    cod_prov = models.IntegerField(default=0, blank=True, null=True)
    cod_com = models.IntegerField(default=0, blank=True, null=True)
    denominazione = models.CharField(max_length=128)
    denominazione_ted = models.CharField(max_length=128, blank=True, null=True)
    territorio = models.CharField(max_length=1, choices=TERRITORIO)
    geom = models.MultiPolygonField(srid=4326, null=True, blank=True)

    objects = models.GeoManager()

    @property
    def nome(self):
        if self.denominazione_ted:
            return "%s - %s" % (self.denominazione, self.denominazione_ted)
        else:
            return "%s" % (self.denominazione)

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = u'Località'
        verbose_name_plural = u'Località'


