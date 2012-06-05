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
    geom = models.MultiPolygonField(srid=4326)

    objects = models.GeoManager()

    def __unicode__(self):
        return "%s (%s)" % (self.denominazione, self.territorio)

    class Meta:
        verbose_name = u'Località'
        verbose_name_plural = u'Località'


