# -*- coding: utf-8 -*-

from django.contrib.gis.db import models
from model_utils import Choices
from progetti.models import Progetto

class Territorio(models.Model):
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

    def progetti(self):
        return self.progetto_set.all()

    @property
    def n_progetti(self):
        return self.progetto_set.count()

    @property
    def progetti_deep(self):
        """
        returns all projects related to this or underlying locations
        (for regions and provinces)
        """
        if self.territorio == self.TERRITORIO.R:
            return Progetto.objects.filter(localizzazione__territorio__cod_reg=self.cod_reg)
        elif self.territorio == self.TERRITORIO.P:
            return Progetto.objects.filter(localizzazione__territorio__cod_reg=self.cod_prov)
        else:
            return self.progetti

    @property
    def n_progetti_deep(self):
        """
        returns number of project related to this or underlying locations
        (for regions and provinces)
        """
        if self.territorio == self.TERRITORIO.R:
            return Progetto.objects.filter(localizzazione__territorio__cod_reg=self.cod_reg).count()
        elif self.territorio == self.TERRITORIO.P:
            return Progetto.objects.filter(localizzazione__territorio__cod_reg=self.cod_prov).count()
        else:
            return self.n_progetti

    @property
    def nome(self):
        if self.denominazione_ted:
            return "%s - %s" % (self.denominazione, self.denominazione_ted)
        else:
            return "%s" % self.denominazione



    def __unicode__(self):
        return self.nome

    @models.permalink
    def get_absolute_url(self):
        return ('territori_%s' % {
            self.TERRITORIO.R: 'regione',
            self.TERRITORIO.P: 'provincia',
            self.TERRITORIO.C: 'comune',
        }[self.territorio], (), {
            'slug': self.denominazione
        })

    class Meta:
        verbose_name = u'Località'
        verbose_name_plural = u'Località'
        ordering = ['denominazione']


