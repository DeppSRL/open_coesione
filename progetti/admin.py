from django.contrib import admin
from progetti.models import *

class ProgrammaAsseObiettivoAdmin(admin.ModelAdmin):
    search_fields = ['descrizione',]
    list_filter = ('tipo_classificazione',)

class LocalizzazioneInline(admin.TabularInline):
    model = Localizzazione
    raw_id_fields = ('progetto', 'territorio', )
    extra = 0

class ProgettoAdmin(admin.ModelAdmin):
    inlines = (LocalizzazioneInline,)
    search_fields = ['^codice_locale',]
    filter_vertical = ('soggetto_set',)


admin.site.register(Progetto, ProgettoAdmin)
admin.site.register(ClassificazioneQSN)
admin.site.register(ClassificazioneAzione)
admin.site.register(ClassificazioneOggetto)
admin.site.register(ProgrammaAsseObiettivo, ProgrammaAsseObiettivoAdmin)
admin.site.register(Tema)
admin.site.register(Fonte)

