# -*- coding: utf-8 -*-

from model_utils import Choices
from progetti.models import Progetto
from django.contrib.gis.db import models
import struct

class TerritoriManager(models.GeoManager):

    def regioni(self):
        return self.get_query_set().filter(territorio= Territorio.TERRITORIO.R )

    def provincie(self):
        return self.get_query_set().filter(territorio= Territorio.TERRITORIO.P )

    def comuni(self):
        return self.get_query_set().filter(territorio= Territorio.TERRITORIO.C )

    def get_from_istat_code(self, istat_code):
        """
        get single record from Territorio, starting from ISTAT code
        ISTAT code has the form RRRPPPCCC, where
         - RRR is the regional code, zero padded
         - PPP is the provincial code, zero padded
         - CCC is the municipal code, zero padded

        if a record in Territorio is not found, then the ObjectDoesNotExist exception is thrown
        """
        if istat_code is None:
            return None

        if len(istat_code) != 9:
            return None

        (cod_reg, cod_prov, cod_com) = struct.unpack('3s3s3s', istat_code)
        return self.get_query_set().get(cod_reg=int(cod_reg), cod_prov=int(cod_prov), cod_com=str(int(cod_prov))+cod_com)

class Territorio(models.Model):
    TERRITORIO = Choices(
        ('C', 'Comune'),
        ('P', 'Provincia'),
        ('R', 'Regione'),
        ('N', 'Nazionale'),
        ('E', 'Estero'),
    )
    cod_reg = models.IntegerField(default=0, blank=True, null=True, db_index=True)
    cod_prov = models.IntegerField(default=0, blank=True, null=True, db_index=True)
    cod_com = models.IntegerField(default=0, blank=True, null=True, db_index=True)
    denominazione = models.CharField(max_length=128)
    denominazione_ted = models.CharField(max_length=128, blank=True, null=True)
    slug = models.SlugField(max_length=256, null=True, blank=True)
    territorio = models.CharField(max_length=1, choices=TERRITORIO, db_index=True)
    geom = models.MultiPolygonField(srid=4326, null=True, blank=True)

    objects = TerritoriManager()

    def progetti(self):
        return self.progetto_set.all()

    @property
    def codice(self):
        if self.territorio == 'C':
            return self.cod_com
        elif self.territorio == 'P':
            return self.cod_prov
        else:
            return self.cod_reg

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
            return Progetto.objects.filter(localizzazione__territorio__cod_prov=self.cod_prov)
        else:
            return Progetto.objects.filter(localizzazione__territorio__cod_com=self.cod_com)

    @property
    def code(self):
        return self.get_cod_dict().values()[0]

    def get_cod_dict(self, prefix=''):
        """
        return a dict with {prefix}cod_{type} key initialized with correct value
        """
        if self.territorio == self.TERRITORIO.R:
            return { '{0}cod_reg'.format(prefix): self.cod_reg }
        elif self.territorio == self.TERRITORIO.P:
            return { '{0}cod_prov'.format(prefix): self.cod_prov }
        elif self.territorio == self.TERRITORIO.C:
            return { '{0}cod_com'.format(prefix) : self.cod_com }

        raise Exception('Territorio non interrogabile %s' % self)

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
        return ('territori_{0}'.format({
            self.TERRITORIO.R: 'regione',
            self.TERRITORIO.P: 'provincia',
            self.TERRITORIO.C: 'comune',
            self.TERRITORIO.N: 'nazionale',
            self.TERRITORIO.E: 'estero',
        }[self.territorio]), (), {
            'slug': self.slug
        })

    class Meta:
        verbose_name = u'Località'
        verbose_name_plural = u'Località'
        ordering = ['denominazione']


