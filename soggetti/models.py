# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models
from django_extensions.db.fields import AutoSlugField
from itertools import chain
from model_utils.models import TimeStampedModel


# class CodiceAteco(models.Model):
#     codice = models.CharField(max_length=16, primary_key=True)
#     descrizione = models.CharField(max_length=1024)
#
#     @property
#     def soggetti(self):
#         return self.soggetto_set.all()
#
#     def __unicode__(self):
#         return u'{}'.format(self.descrizione)
#
#     class Meta:
#         verbose_name = 'Codice ATECO'
#         verbose_name_plural = 'Codici ATECO'


# class FormaGiuridica(models.Model):
#     codice = models.CharField(max_length=8, primary_key=True)
#     denominazione = models.CharField(max_length=255)
#
#     @property
#     def soggetti(self):
#         return self.soggetto_set.all()
#
#     def __unicode__(self):
#         return u'{}'.format(self.denominazione)
#
#     class Meta:
#         verbose_name = 'Forma giuridica'
#         verbose_name_plural = 'Forme giuridiche'


# class SoggettoManager(models.Manager):
#     def get_query_set(self):
#         return models.query.QuerySet(self.model, using=self._db).filter(ruolo__progetto__active_flag=True).distinct()


class Soggetto(TimeStampedModel):
    codice_fiscale = models.CharField(max_length=16)
    denominazione = models.CharField(max_length=512)
    slug = AutoSlugField(populate_from='denominazione_univoca', max_length=300, unique=True, db_index=True)
    # forma_giuridica = models.ForeignKey(FormaGiuridica, null=True, blank=True, db_column='forma_giuridica')
    # codice_ateco = models.ForeignKey(CodiceAteco, null=True, blank=True, db_column='codice_ateco')
    territorio = models.ForeignKey('territori.Territorio', null=True)
    # rappresentante_legale = models.CharField(max_length=300, null=True, blank=True)
    indirizzo = models.CharField(max_length=300, null=True, blank=True)
    cap = models.CharField(max_length=5, null=True, blank=True)
    privacy_flag = models.BooleanField(default=False)

    @property
    def denominazione_univoca(self):
        return (u'{} {}'.format(self.denominazione, '' if self.codice_fiscale == '*CODICE FISCALE*' else self.codice_fiscale)).strip()

    @property
    def progetti(self):
        return self.progetto_set.all()

    @property
    def n_progetti(self):
        return self.progetto_set.count()

    @property
    def has_progetti(self):
        # return self.n_progetti > 0
        try:
            a = self.progetti[0]
            return True
        except IndexError:
            return False

    @property
    def ruoli(self):
        return self.ruolo_set.all()

    @property
    def regioni(self):
        """
        Returns the set of different regions where this soggetto has progetti localized
        """
        return set(chain.from_iterable([list(p.regioni) for p in self.progetti]))

    def get_absolute_url(self):
        return reverse('soggetti_soggetto', kwargs={'slug': self.slug})

    def __unicode__(self):
        return u'{}'.format(self.denominazione)

    class Meta:
        verbose_name_plural = 'Soggetti'
        unique_together = ('denominazione', 'codice_fiscale')
        index_together = [
            ['denominazione', 'codice_fiscale']
        ]
