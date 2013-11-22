from haystack.indexes import *
from haystack import site

from progetti.models import Ruolo, Tema, Progetto
from soggetti.models import Soggetto

class SoggettoIndex(SearchIndex):
    slug = CharField(model_attr='slug', indexed=False)
    text = CharField(document=True, use_template=True)
    denominazione = CharField(model_attr='denominazione', indexed=False)
    codice_fiscale = CharField(model_attr='codice_fiscale', indexed=False)
    territorio_com = MultiValueField(indexed=True, stored=True)
    territorio_prov = MultiValueField(indexed=True, stored=True)
    territorio_reg = MultiValueField(indexed=True, stored=True)
    tema_slug = MultiValueField(indexed=False, stored=True)
    ruolo_descr = MultiValueField(indexed=False, stored=True)

    # faceting fields
    ruolo = FacetMultiValueField()
    tema = FacetMultiValueField()
    costo = FacetFloatField()
    n_progetti = FacetIntegerField()

    # search result format is pre-rendered during index phase
    rendered = CharField(use_template=True, indexed=False)

    def prepare_ruolo(self, obj):
        """
        Returns all ruoli (as code) for the given object
        """
        return [r['ruolo'] for r in Ruolo.objects.filter(soggetto=obj).values('ruolo').distinct()]

    def prepare_ruolo_descr(self, obj):
        """
        Returns all ruoli (as descriptions) for the given subject
        """
        return [Ruolo.inv_ruoli_dict()[r['ruolo']] for r in Ruolo.objects.filter(soggetto=obj).values('ruolo').distinct()]

    def prepare_tema(self, obj):
        return [t['codice'] for t in Tema.objects.filter(tema_set__progetto_set__soggetto_set=obj).values('codice').distinct()]

    def prepare_tema_slug(self, obj):
        return [t['slug'] for t in Tema.objects.filter(tema_set__progetto_set__soggetto_set=obj).values('slug').distinct()]


    def prepare_costo(self, obj):
        return Progetto.objects.totale_costi(soggetto=obj)

    def prepare_n_progetti(self, obj):
        return Progetto.objects.totale_progetti(soggetto=obj)

    def prepare_territorio_reg(self, obj):
        if obj.territorio:
            return obj.territorio.cod_reg

    def prepare_territorio_prov(self, obj):
        if obj.territorio:
            return obj.territorio.cod_prov

    def prepare_territorio_com(self, obj):
        if obj.territorio:
            return obj.territorio.cod_com


site.register(Soggetto, SoggettoIndex)