from django.contrib.gis.db import models
from territori.models import Territorio

class TerritoriManager(models.GeoManager):

    def regioni(self):
        return self.get_query_set().filter(territorio= Territorio.TERRITORIO.R )

    def provincie(self):
        return self.get_query_set().filter(territorio= Territorio.TERRITORIO.P )

    def comuni(self):
        return self.get_query_set().filter(territorio= Territorio.TERRITORIO.C )