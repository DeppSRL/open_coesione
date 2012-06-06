import datetime
from haystack.indexes import *
from haystack import site

from progetti.models import Progetto

from django.utils.translation import activate
from django.conf import settings

class ProgettoIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)

    # faceting fields
    tipo_operazione = FacetCharField( )
    priorita = FacetCharField( )

    # stored fields, used not to touch DB
    # while showing results
    # url = CharField(indexed=False, stored=True)
    titolo = CharField(indexed=False, stored=True, model_attr='titolo_progetto')

    def prepare_tipo_operazione(self, obj):
        return obj.tipo_operazione

    def prepare_priorita(self, obj):
        return obj.classificazione_qsn.codice.split('.')[0]


site.register(Progetto, ProgettoIndex)