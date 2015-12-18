# -*- coding: utf-8 -*-
from django.db import models
from progetti.models import Tema


# class IndicatoreRegionaleQuerySet(models.query.QuerySet):
#     def used(self):
#         from django.conf import settings
#         return self.filter(indicatore__in=settings.INDICATORI_VALIDI, ripartizione__in=range(1, 21) + [23])


# class IndicatoreRegionaleManager(models.Manager):
#     def get_query_set(self):
#         return IndicatoreRegionaleQuerySet(self.model, using=self._db)
#
#     def used(self):
#         return self.get_query_set().used()


class ChartsQuerySet(models.query.QuerySet):
    def with_value(self):
        return self.filter(indicatori_regionali__isnull=False).distinct()


class ChartsManager(models.Manager):
    def get_query_set(self):
        return ChartsQuerySet(self.model, using=self._db)

    def with_value(self):
        return self.get_query_set().with_value()


class Indicatore(models.Model):
    codice = models.CharField(max_length=3, primary_key=True)
    titolo = models.CharField(max_length=150)
    sottotitolo = models.CharField(max_length=500)
    tema = models.ForeignKey(Tema, related_name='indicatori', limit_choices_to={'tipo_tema': Tema.TIPO.sintetico})

    objects = ChartsManager()

    def __unicode__(self):
        return u'{} - [{}] {} ({})'.format(self.tema.descrizione, self.codice, self.titolo, self.sottotitolo)


class Ripartizione(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    descrizione = models.CharField(max_length=100)

    objects = ChartsManager()

    def __unicode__(self):
        return u'[{}] {}'.format(self.id, self.descrizione)


class IndicatoreRegionale(models.Model):
    indicatore = models.ForeignKey(Indicatore, related_name='indicatori_regionali')
    ripartizione = models.ForeignKey(Ripartizione, related_name='indicatori_regionali')
    anno = models.CharField(max_length=4)
    valore = models.CharField(max_length=20)
    da_eliminare = models.BooleanField(default=False, db_index=True)

    # objects = IndicatoreRegionaleManager()

    def __unicode__(self):
        return u'{} / {} / {}: {}'.format(self.indicatore, self.ripartizione, self.anno, self.valore)

    class Meta:
        unique_together = ('indicatore', 'ripartizione', 'anno')
        index_together = [
            ['indicatore', 'ripartizione', 'anno'],
        ]
