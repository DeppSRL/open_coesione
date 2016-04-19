# -*- coding: utf-8 -*-
import re
import struct
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property
from django_extensions.db.fields import AutoSlugField
from model_utils import Choices


class TerritorioManager(models.GeoManager):
    def nazione(self):
        return self.get_query_set().get(territorio=self.model.TERRITORIO.N)

    def regioni(self, with_nation=False):
        codes = [self.model.TERRITORIO.R]
        if with_nation:
            codes.append(self.model.TERRITORIO.N)
            codes.append(self.model.TERRITORIO.E)
        return self.get_query_set().filter(territorio__in=codes)

    def provincie(self):
        return self.get_query_set().filter(territorio=self.model.TERRITORIO.P)

    def comuni(self):
        return self.get_query_set().filter(territorio=self.model.TERRITORIO.C)

    @cached_property
    def regioni_by_cod(self):
        return {o.cod_reg: o for o in self.regioni()}

    @cached_property
    def provincie_by_cod(self):
        return {o.cod_prov: o for o in self.provincie()}

    def get_from_istat_code(self, istat_code):
        """
        Get single record from Territorio, starting from ISTAT code
        ISTAT code has the form RRRPPPCCC, where
         - RRR is the regional code, zero padded
         - PPP is the provincial code, zero padded
         - CCC is the municipal code, zero padded

        If a record in Territorio is not found, then the ObjectDoesNotExist exception is thrown
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
    denominazione = models.CharField(max_length=128, db_index=True)
    denominazione_ted = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    slug = AutoSlugField(populate_from='nome_per_slug', max_length=256, unique=True, db_index=True)
    territorio = models.CharField(max_length=1, choices=TERRITORIO, db_index=True)
    geom = models.MultiPolygonField(srid=4326, null=True, blank=True)
    popolazione_totale = models.IntegerField(null=True, blank=True)
    popolazione_maschile = models.IntegerField(null=True, blank=True)
    popolazione_femminile = models.IntegerField(null=True, blank=True)

    objects = TerritorioManager()

    @property
    def nome(self):
        if self.denominazione_ted:
            return u'{} - {}'.format(self.denominazione, self.denominazione_ted)
        else:
            return u'{}'.format(self.denominazione)

    @property
    def nome_completo(self):
        if self.is_comune or self.is_provincia:
            return u'{} di {}'.format(self.get_territorio_display(), self.nome)
        elif self.is_regione:
            return u'{} {}'.format(self.get_territorio_display(), self.nome)
        else:
            return u'{}'.format(self.nome)

    @property
    def nome_con_provincia(self):
        if self.is_provincia:
            return u'{} (Provincia)'.format(self.nome)
        else:
            return u'{}'.format(self.nome)

    @property
    def nome_per_slug(self):
        return u'{} {}'.format(self.denominazione, self.get_territorio_display())

    @property
    def ambito_territoriale(self):
        """
        Returns: a Region (for C,P or R), Nazionale, or Estero
        """
        if self.is_regione:
            return self.nome
        elif self.regione:
            return self.regione.nome
        else:
            return self.get_territorio_display()

    @cached_property
    def regione(self):
        if self.is_comune or self.is_provincia:
            return self.__class__.objects.regioni_by_cod[self.cod_reg]
        else:
            return None

    @cached_property
    def provincia(self):
        if self.is_comune:
            return self.__class__.objects.provincie_by_cod[self.cod_prov]
        else:
            return None

    @property
    def codice(self):
        if self.is_comune:
            return self.cod_com
        elif self.is_provincia:
            return self.cod_prov
        else:
            return self.cod_reg

    def progetti(self):
        return self.progetto_set.all()

    @property
    def n_progetti(self):
        return self.progetto_set.count()

    @property
    def code(self):
        return self.get_cod_dict().values()[0]

    def get_cod_dict(self, prefix=''):
        """
        Return a dict with {prefix}cod_{type} key initialized with correct value
        """
        if self.is_comune:
            return {'{}cod_com'.format(prefix): self.cod_com}
        elif self.is_provincia:
            return {'{}cod_prov'.format(prefix): self.cod_prov}
        elif self.is_regione:
            return {'{}cod_reg'.format(prefix): self.cod_reg}
        elif self.is_nazionale:
            return {'{}cod_reg'.format(prefix): 0}
        elif self.is_estero:
            return {'{}pk'.format(prefix): self.pk}

        raise Exception('Territorio non interrogabile {}'.format(self))

    def get_hierarchy(self):
        """
        Returns the list of parent objects (self included)
        """
        hierarchy = [self]
        if self.provincia:
            hierarchy.insert(0, self.provincia)
            if self.regione:
                hierarchy.insert(0, self.regione)

        return hierarchy

    def get_breadcrumbs(self):
        return [(territorio.denominazione, territorio.get_absolute_url()) for territorio in self.get_hierarchy()]

    def get_progetti_search_url(self, **kwargs):
        """
        Returns the correct search url in progetti faceted navigation.
        Can be used with optional filters:
        tema=TemaInstance
        natura=ClassificazioneAzioneInstance
        """
        search_url = reverse('progetti_search') + '?q='

        if 'tema' in kwargs:
            tema = kwargs['tema']
            search_url += '&selected_facets=tema:{}'.format(tema.codice)

        if 'natura' in kwargs:
            natura = kwargs['natura']
            search_url += '&selected_facets=natura:{}'.format(natura.codice)

        if 'programma' in kwargs:
            programma = kwargs['programma']
            search_url += '&fonte_fin={}'.format(programma.codice)

        if 'gruppo_programmi' in kwargs:
            gruppo_programmi = kwargs['gruppo_programmi']
            search_url += '&gruppo_programmi={}'.format(gruppo_programmi.codice)

        for t in self.get_hierarchy():
            d = t.get_cod_dict()
            key = d.keys()[0]
            search_url += '&territorio{}={}'.format(key[3:], d[key])

        return search_url

    def get_absolute_url(self):
        url_name = 'territori_{}'.format(self.get_territorio_display().lower())

        if self.is_nazionale or self.is_estero:
            return reverse(url_name)
        else:
            return reverse(url_name, kwargs={'slug': self.slug})

    def __getattr__(self, item):
        match = re.search('^is_({})$'.format('|'.join(dict(self.__class__.TERRITORIO).values()).lower()), item)
        if match:
            return self.get_territorio_display().lower() == match.group(1)
        else:
            raise AttributeError('{0!r} object has no attribute {1!r}'.format(self.__class__.__name__, item))

    def __unicode__(self):
        return u'{}'.format(self.nome)

    class Meta:
        verbose_name = u'Località'
        verbose_name_plural = u'Località'
        ordering = ['denominazione']
