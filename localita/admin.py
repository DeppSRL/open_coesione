from django.contrib.gis import admin
from models import Localita

class LocalitaAdmin(admin.OSMGeoAdmin):
    list_filter = ('territorio',)
    search_fields = ('denominazione',)


admin.site.register(Localita, LocalitaAdmin)
