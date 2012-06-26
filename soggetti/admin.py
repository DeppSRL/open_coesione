from django.contrib import admin
from soggetti.models import *

class SoggettoAdmin(admin.ModelAdmin):
    search_fields = ['^denominazione',]
    list_filter = ('ruolo',)

admin.site.register(Soggetto, SoggettoAdmin)
admin.site.register(FormaGiuridica)