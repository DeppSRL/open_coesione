from django.contrib import admin
from tinymce.widgets import TinyMCE
from open_coesione.utils import export_select_fields_csv_action
from progetti.models import *
from open_coesione.admin import FileInline, LinkInline, TinyMCEEnabledForm, common_mce_attrs


# class ProgrammaExtraInfoAdminForm(TinyMCEEnabledForm):
#     class Meta:
#         widgets = {
#             'descrizione_estesa': TinyMCE(mce_attrs=common_mce_attrs)
#         }


class ProgrammaAdminForm(TinyMCEEnabledForm):
    class Meta:
        widgets = {
            'descrizione_estesa': TinyMCE(mce_attrs=common_mce_attrs)
        }


class LocalizzazioneInline(admin.TabularInline):
    model = Localizzazione
    raw_id_fields = ('progetto', 'territorio',)
    extra = 0


class DeliberaCIPEInline(admin.TabularInline):
    model = ProgettoDeliberaCIPE
    raw_id_fields = ('delibera',)
    extra = 0


class CUPSInline(admin.TabularInline):
    model = CUP
    extra = 0


# class ProgrammaExtraInfoInline(admin.StackedInline):
#     model = ProgrammaAsseObiettivoExtraInfo
#     inlines = [DocumentoInline, URLInline]
#
#     def __init__(self, *args, **kwargs):
#         super(ProgrammaExtraInfoInline, self).__init__(*args, **kwargs)
#         self.model = eval(self.parent_model.__name__ + 'ExtraInfo')


class ProgrammaAdmin(admin.ModelAdmin):
    list_display = ['codice', 'descrizione']
    search_fields = ['descrizione', 'codice']
    list_filter = ('tipo_classificazione',)
    inlines = [FileInline, LinkInline]
    form = ProgrammaAdminForm

    # def has_add_permission(self, request):
    #     return request.user.is_superuser

    # def has_delete_permission(self, request, obj=None):
    #     return request.user.is_superuser

    # def get_actions(self, request):
    #     actions = super(ProgrammaAdmin, self).get_actions(request)
    #     if not request.user.is_superuser:
    #         if 'delete_selected' in actions:
    #             del actions['delete_selected']
    #     return actions

    def queryset(self, request):
        qs = super(ProgrammaAdmin, self).queryset(request)
        if not request.user.is_superuser:
            qs = qs.programmi()
        return qs

    def get_list_filter(self, request):
        if not request.user.is_superuser:
            return ()
        return self.list_filter

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if not request.user.is_superuser:
            self.fields = ('codice', 'descrizione', 'descrizione_estesa')
            self.readonly_fields = ('codice', 'descrizione')

        return super(ProgrammaAdmin, self).change_view(request, object_id, form_url, extra_context)


# class ProgrammaExtraInfoAdmin(admin.ModelAdmin):
#     list_select_related = True
#     list_display = ['codice', 'descrizione']
#     search_fields = ['programma__descrizione', 'programma__codice']
#     list_filter = ('programma__tipo_classificazione',)
#     exclude = ('programma',)
#     inlines = [DocumentoInline, URLInline]
#     form = ProgrammaExtraInfoAdminForm
#
#     def codice(self, obj):
#         return obj.programma.codice
#
#     def descrizione(self, obj):
#         return obj.programma.descrizione
#
#     def has_add_permission(self, request):
#         return False
#
#     def has_delete_permission(self, request, obj=None):
#         return False
#
#     def get_actions(self, request):
#         actions = super(ProgrammaExtraInfoAdmin, self).get_actions(request)
#         if 'delete_selected' in actions:
#             del actions['delete_selected']
#         return actions


class ProgettoAdmin(admin.ModelAdmin):
    inlines = (LocalizzazioneInline, DeliberaCIPEInline, CUPSInline)
    search_fields = ['^codice_locale', 'slug']
    filter_vertical = ('soggetto_set',)
    list_filter = ('cipe_flag',)

    # modify fields list, for superuser
    def change_view(self, request, object_id, form_url='', extra_context=None):

        if not request.user.is_superuser:
            self.fields = ('codice_locale', 'cup', 'titolo_progetto', 'descrizione',)
            self.readonly_fields = ('codice_locale', 'cup', 'titolo_progetto')

        return super(ProgettoAdmin, self).change_view(request, object_id, form_url, extra_context)

    # trick to save related formsets before the main form
    # http://stackoverflow.com/questions/14858559/save-the-related-objects-before-the-actual-object-being-edited-on-django-admin

    def save_model(self, request, obj, form, change):
        pass

    def save_formset(self, request, form, formset, change):
        formset.save()  # this will save the children
        form.instance.save()  # form.instance is the parent


class TemaAdmin(admin.ModelAdmin):
    list_display = ('codice', 'descrizione', 'priorita')
    list_filter = ('tipo_tema',)
    list_editable = ('priorita',)


class ClassificazioneAdmin(admin.ModelAdmin):
    list_filter = ('tipo_classificazione',)


class ClassificazioneAzioneAdmin(ClassificazioneAdmin):
    list_display = ('codice', 'descrizione', 'priorita')
    list_editable = ('priorita',)


class SegnalazioneAdmin(admin.ModelAdmin):
    list_display = ('email', 'cup', 'is_cipe', 'modified')
    list_filter = ('is_cipe',)
    search_fields = ('email', 'cup')
    fieldsets = (
        (None, {
            'fields': ('pubblicato', 'come_lo_conosci', 'come_lo_conosci_altro', ('cup', 'is_cipe'))
        }),
        ('Persona', {
            'fields': ('organizzazione', 'utente', 'email'),
            'classes': ('collapse',)
        }),
        ('Descrizione', {
            'fields': ('descrizione', 'come_migliorare', 'risultati_conseguiti', 'effetti_sul_territorio',
                       'cosa_piace', 'cosa_non_piace', 'quanto_utile'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['come_lo_conosci', 'come_lo_conosci_altro', 'cup', 'is_cipe', 'organizzazione', 'utente', 'email',
                       'descrizione', 'come_migliorare', 'risultati_conseguiti', 'effetti_sul_territorio',
                       'cosa_piace', 'cosa_non_piace', 'quanto_utile']
    actions = [
        export_select_fields_csv_action("Esporta i selezionati in formato CSV",
             fields=[
                 ('cup', 'Codice CUP del progetto'),
                 ('is_cipe', 'Se CIPE'),
                 ('modified', 'Ultima modifica'),
                 ('pubblicato', 'Pubblicato'),
                 ('come_lo_conosci', 'Come lo conosci'),
                 ('come_lo_conosci_altro', 'Note su come hai conosciuto il progetto'),
                 ('organizzazione', 'Organizzazione'),
                 ('utente', 'Nome e cognome'),
                 ('descrizione', 'Descrizione'),
                 ('come_migliorare', 'Come migliorare'),
                 ('risultati_conseguiti', 'Risultati conseguiti'),
                 ('effetti_sul_territorio', 'Effetti sul territorio'),
                 ('cosa_piace', 'Cosa piace'),
                 ('cosa_non_piace', 'Cosa non piace'),
                 ('quanto_utile', 'Quanto utile'),
             ],
             header=True
        ),
    ]


admin.site.register(Progetto, ProgettoAdmin)
admin.site.register(ClassificazioneQSN, ClassificazioneAdmin)
admin.site.register(ClassificazioneAzione, ClassificazioneAzioneAdmin)
admin.site.register(ClassificazioneOggetto, ClassificazioneAdmin)
admin.site.register(ProgrammaAsseObiettivo, ProgrammaAdmin)
admin.site.register(ProgrammaLineaAzione, ProgrammaAdmin)
# admin.site.register(ProgrammaAsseObiettivoExtraInfo, ProgrammaExtraInfoAdmin)
# admin.site.register(ProgrammaLineaAzioneExtraInfo, ProgrammaExtraInfoAdmin)
admin.site.register(Tema, TemaAdmin)
admin.site.register(Fonte)
admin.site.register(DeliberaCIPE)
admin.site.register(SegnalazioneProgetto, SegnalazioneAdmin)
