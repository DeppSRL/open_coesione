# -*- coding: utf-8 -*-
from haystack.indexes import *
from haystack import site
from progetti.models import Progetto, Ruolo, Tema
from soggetti.models import Soggetto


class SoggettoIndex(SearchIndex):
    text = CharField(document=True, use_template=True, stored=False)

    territorio_com = MultiValueField(stored=False)
    territorio_prov = MultiValueField(stored=False)
    territorio_reg = MultiValueField(stored=False)

    ruolo = FacetMultiValueField()
    tema = FacetMultiValueField(stored=False)

    costo = FacetFloatField()
    n_progetti = FacetIntegerField()

    def prepare_territorio_com(self, obj):
        if obj.territorio:
            return obj.territorio.cod_com

    def prepare_territorio_prov(self, obj):
        if obj.territorio:
            return obj.territorio.cod_prov

    def prepare_territorio_reg(self, obj):
        if obj.territorio:
            return obj.territorio.cod_reg

    def prepare_ruolo(self, obj):
        return Ruolo.objects.filter(soggetto=obj).values_list('ruolo', flat=True).distinct()

    def prepare_tema(self, obj):
        return Tema.objects.filter(tema_set__progetto_set__soggetto_set=obj).values_list('codice', flat=True).distinct()

    def prepare_costo(self, obj):
        return Progetto.objects.myfilter(soggetto=obj).totali()['totale_costi']

    def prepare_n_progetti(self, obj):
        return Progetto.objects.myfilter(soggetto=obj).totali()['totale_progetti']

    def index_queryset(self):
        return self.model._default_manager.select_related('territorio')


site.register(Soggetto, SoggettoIndex)
