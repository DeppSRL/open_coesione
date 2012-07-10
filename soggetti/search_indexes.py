import datetime
from haystack.indexes import *
from haystack import site

from progetti.models import Ruolo, Tema, Progetto
from soggetti.models import Soggetto

from django.utils.translation import activate
from django.conf import settings

class SoggettoIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    # territorio = MultiValueField(indexed=True, stored=True)

    # faceting fields
    ruolo = FacetMultiValueField()
    tema = FacetMultiValueField()
    finanziamenti = FacetFloatField()
    n_progetti = FacetIntegerField()

    # search result format is pre-rendered during index phase
    rendered = CharField(use_template=True, indexed=False)

    def prepare_ruolo(self, obj):
        return [r['ruolo'] for r in Ruolo.objects.filter(soggetto=obj).values('ruolo').distinct()]

    def prepare_tema(self, obj):
        return [t['codice'] for t in Tema.objects.filter(tema_set__progetto_set__soggetto_set=obj).distinct().values('codice')]

    def prepare_finanziamenti(self, obj):
        return Progetto.objects.totale_costi(soggetto=obj)

    def prepare_n_progetti(self, obj):
        return Progetto.objects.totale_progetti(soggetto=obj)

    def prepare_territorio(self, obj):
        return obj.territorio


site.register(Soggetto, SoggettoIndex)