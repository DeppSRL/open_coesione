# -*- coding: utf-8 -*-
from django.utils.functional import cached_property
from haystack.indexes import *
from haystack import site
from progetti.models import Progetto, Ruolo, Tema
from soggetti.models import Soggetto


class SoggettoIndex(SearchIndex):
    # slug = CharField(model_attr='slug', indexed=False)
    # privacy_flag = CharField(model_attr='privacy_flag', stored=False)
    text = CharField(document=True, use_template=True, stored=False)
    # denominazione = CharField(model_attr='denominazione', indexed=False)
    # codice_fiscale = CharField(model_attr='codice_fiscale', indexed=False)
    territorio_com = MultiValueField(stored=False)
    territorio_prov = MultiValueField(stored=False)
    territorio_reg = MultiValueField(stored=False)
    # tema_slug = MultiValueField(indexed=False, stored=True)
    # ruolo_descr = MultiValueField(indexed=False, stored=True)

    # faceting fields
    ruolo = FacetMultiValueField()
    tema = FacetMultiValueField(stored=False)
    costo = FacetFloatField()
    n_progetti = FacetIntegerField()

    # search result format is pre-rendered during index phase
    # rendered = CharField(use_template=True, indexed=False)

    def prepare_ruolo(self, obj):
        """
        Returns all ruoli (as code) for the given object
        """
        return Ruolo.objects.filter(soggetto=obj).values_list('ruolo', flat=True).distinct()

    # def prepare_ruolo_descr(self, obj):
    #     """
    #     Returns all ruoli (as descriptions) for the given subject
    #     """
    #     return [Ruolo.inv_ruoli_dict()[r['ruolo']] for r in Ruolo.objects.filter(soggetto=obj).values('ruolo').distinct()]

    def prepare_tema(self, obj):
        return Tema.objects.filter(tema_set__progetto_set__soggetto_set=obj).values_list('codice', flat=True).distinct()

    # def prepare_tema_slug(self, obj):
    #     return [t['slug'] for t in Tema.objects.filter(tema_set__progetto_set__soggetto_set=obj).values('slug').distinct()]

    def prepare_costo(self, obj):
        return self._totali(obj)['totale_costi']

    def prepare_n_progetti(self, obj):
        return self._totali(obj)['totale_progetti']

    def _totali(self, obj):
        return Progetto.objects.dict_totali(soggetto=obj)

    def prepare_territorio_reg(self, obj):
        if obj.territorio:
            return obj.territorio.cod_reg

    def prepare_territorio_prov(self, obj):
        if obj.territorio:
            return obj.territorio.cod_prov

    def prepare_territorio_com(self, obj):
        if obj.territorio:
            return obj.territorio.cod_com

    def index_queryset(self):
        return self.model._default_manager.select_related('territorio')


site.register(Soggetto, SoggettoIndex)
