from django.contrib import admin
from mct_progetti.models import *

class LocalizzazioneInline(admin.TabularInline):
    model = Localizzazione
    raw_id_fields = ('progetto', 'localita', )
    extra = 0

class ProgettoAdmin(admin.ModelAdmin):
    inlines = (LocalizzazioneInline,)
    search_fields = ['^codice_locale',]
    filter_vertical = ('soggetto_set',)


class SoggettoAdmin(admin.ModelAdmin):
    search_fields = ['^denominazione',]
    list_filter = ('ruolo',)

admin.site.register(Progetto, ProgettoAdmin)
admin.site.register(ClassificazioneQSN)
admin.site.register(ClassificazioneAzione)
admin.site.register(ClassificazioneOggetto)
admin.site.register(ProgrammaAsseObiettivo)
admin.site.register(Tema)
admin.site.register(Intesa)
admin.site.register(Localita)
admin.site.register(Soggetto, SoggettoAdmin)
