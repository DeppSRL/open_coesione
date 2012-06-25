import datetime
from haystack.indexes import *
from haystack import site

from progetti.models import Progetto

from django.utils.translation import activate
from django.conf import settings

# user RealTimeSearchIndex once online

class ProgettoIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    # faceting fields
    natura = FacetCharField( )
    tema = FacetCharField( )

    # search result format is pre-rendered during index phase
    rendered = CharField(use_template=True, indexed=False)

    def prepare_natura(self, obj):
        return obj.classificazione_azione.codice.split('.')[0]

    def prepare_tema(self, obj):
        return obj.tema.codice.split('.')[0]


site.register(Progetto, ProgettoIndex)