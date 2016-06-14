# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.filters import AllValuesFieldListFilter
from models import Fonte, Contatto, Iscrizione
from open_coesione.utils import export_select_fields_csv_action


class FonteListFilter(AllValuesFieldListFilter):
    """
    Must use a custom filter class, just to change the human readable title in the right sidebar
    """
    def __init__(self, field, request, params, model, model_admin, field_path):
        super(FonteListFilter, self).__init__(field, request, params, model, model_admin, field_path)
        self.title = 'fonte'


class SourceAdmin(admin.ModelAdmin):
    pass


class SubscriptionInline(admin.StackedInline):
    readonly_fields = ("created_at",)
    model = Iscrizione
    extra = 0


class ContactAdmin(admin.ModelAdmin):
    inlines = [SubscriptionInline, ]


class SubscriptionAdmin(admin.ModelAdmin):
    list_filter = (('source__name', FonteListFilter), 'user_type', 'created_at')
    search_fields = ('contact__email', 'contact__first_name', 'contact__last_name', 'role', 'title')
    list_display = ('email', 'user_type', 'role', 'title', 'created_at', 'source')
    actions = [
        export_select_fields_csv_action(
            'Esporta i selezionati in formato CSV',
            fields=[
                ('contact__first_name', 'Nome'),
                ('contact__last_name', 'Cognome'),
                ('contact__email', 'Email'),
                ('pippo', 'Tipologia di utente'),
                ('notes', 'Note'),
            ],
            header=True
        ),
    ]


admin.site.register(Fonte, SourceAdmin)
admin.site.register(Contatto, ContactAdmin)
admin.site.register(Iscrizione, SubscriptionAdmin)
