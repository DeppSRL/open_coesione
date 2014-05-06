# -*- coding: utf-8 -*-
from django.db import models
from model_utils.models import TimeStampedModel

from itertools import chain


class CodiceAteco(models.Model):
    codice = models.CharField(max_length=16, primary_key=True)
    descrizione = models.CharField(max_length=1024)

    @property
    def soggetti(self):
        return self.soggetto_set.all()

    def __unicode__(self):
        return u"%s" % (self.descrizione,)

    class Meta:
        verbose_name = "Codice ATECO"
        verbose_name_plural = "Codici ATECO"


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


class SoggettiManager(models.Manager):
    def get_query_set(self):
        return models.query.QuerySet(self.model, using=self._db).filter(ruolo__progetto__active_flag=True).distinct()

class Soggetto(TimeStampedModel):
    codice_fiscale = models.CharField(max_length=16)
    denominazione = models.CharField(max_length=512, db_index=True)
    slug = models.CharField(max_length=300, blank=True, null=True)
    forma_giuridica = models.ForeignKey(FormaGiuridica,
                                        db_column='forma_giuridica', null=True, blank=True)
    codice_ateco = models.ForeignKey(CodiceAteco,
                                     db_column='codice_ateco', null=True, blank=True)
    territorio = models.ForeignKey('territori.Territorio', null=True)
    rappresentante_legale = models.CharField(max_length=300, null=True, blank=True)
    indirizzo = models.CharField(max_length=300, null=True, blank=True)
    cap = models.CharField(max_length=5, null=True, blank=True)

    objects = models.Manager()
    filteredobjects = SoggettiManager()
    fullobjects = models.Manager()

    @property
    def progetti(self):
        return self.progetto_set.all()

    @property
    def n_progetti(self):
        return self.progetto_set.count()

    @property
    def has_progetti(self):
        try:
            a = self.progetti[0]
            return True
        except IndexError:
            return False

        # return self.n_progetti > 0


    @property
    def ruoli(self):
        return self.ruolo_set.all()

    @property
    def regioni(self):
        """
        Returns the set of different regions where this soggetto has progetti localized
        """
        return set(chain.from_iterable([list(p.regioni) for p in self.progetti]))

    def __unicode__(self):
        return u"%s" % (self.denominazione, )

    @models.permalink
    def get_absolute_url(self):
        return ('soggetti_soggetto', (), {
            'slug': self.slug
        })

    class Meta:
        verbose_name_plural = "Soggetti"
