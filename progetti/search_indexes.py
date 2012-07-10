import datetime
from haystack.indexes import *
from haystack import site
from oc_search.fields import L10NCharField

from progetti.models import Progetto

from django.utils.translation import activate
from django.conf import settings

# user RealTimeSearchIndex once online

class ProgettoIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    territorio = MultiValueField(indexed=True, stored=True)

    # faceting fields
    natura = FacetCharField( )
    tema = FacetCharField( )
    data_inizio = FacetDateField(model_attr='data_inizio_effettiva')
    costo = FacetFloatField(model_attr='fin_totale_pubblico')

    # search result format is pre-rendered during index phase
    rendered = L10NCharField(use_template=True, indexed=False)

    def prepare_natura(self, obj):
        return obj.classificazione_azione.codice.split('.')[0]

    def prepare_tema(self, obj):
        return obj.tema.codice.split('.')[0]

    def prepare_territorio(self, obj):
        return [t.pk for t in list(obj.territori)]


site.register(Progetto, ProgettoIndex)