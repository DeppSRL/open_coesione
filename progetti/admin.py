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

    # modify fields list, for superuser
    def change_view(self, request, object_id, form_url='', extra_context=None):

        if not request.user.is_superuser:
            self.fields = ('codice_locale', 'cup', 'titolo_progetto', 'descrizione', )
            self.readonly_fields = ('codice_locale', 'cup', 'titolo_progetto')

        return super(ProgettoAdmin, self).change_view(request, object_id)

class TemaAdmin(admin.ModelAdmin):
    list_filter = ('tipo_tema',)

class ClassificazioneAdmin(admin.ModelAdmin):
    list_filter = ('tipo_classificazione',)

class ClassificazioneAzioneAdmin(ClassificazioneAdmin):
    list_display = ('codice', 'descrizione', 'priorita')


admin.site.register(Progetto, ProgettoAdmin)
admin.site.register(ClassificazioneQSN, ClassificazioneAdmin)
admin.site.register(ClassificazioneAzione, ClassificazioneAzioneAdmin)
admin.site.register(ClassificazioneOggetto, ClassificazioneAdmin)
admin.site.register(ProgrammaAsseObiettivo, ProgrammaAsseObiettivoAdmin)
admin.site.register(Tema, TemaAdmin)
admin.site.register(Fonte)

