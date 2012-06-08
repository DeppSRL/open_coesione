from django.contrib.gis import admin
from models import Territorio

class TerritorioAdmin(admin.OSMGeoAdmin):
    list_filter = ('territorio',)
    search_fields = ('denominazione',)


admin.site.register(Territorio, TerritorioAdmin)
