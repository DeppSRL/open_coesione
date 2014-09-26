from django.contrib import admin
from django.contrib.admin.filters import RelatedFieldListFilter, AllValuesFieldListFilter
from django.http import HttpResponse
from .models import Fonte, Contatto, Iscrizione
import csv


def export_select_fields_csv_action(description="Export selected objects as CSV file",
                                    fields=None, exclude=None, header=True):
    """
    This function returns an export csv action

    'fields' is a list of tuples denoting the field and label to be exported. Labels
    make up the header row of the exported file if header=True.

        fields=[
                ('field1', 'label1'),
                ('field2', 'label2'),
                ('field3', 'label3'),
            ]
    You can use the ORM lookup '__' syntax to access related fields,
    but the existance of the field is not checked in advance.
    Errors are trapped in this case and '' is returned as value.

    'exclude' is a flat list of fields to exclude. If 'exclude' is passed,
    'fields' will not be used. Either use 'fields' or 'exclude.'

        exclude=['field1', 'field2', field3]

    'header' is whether or not to output the column names as the first row

    Based on: http://djangosnippets.org/snippets/2020/
    """
    def extended_getattr(obj, attribute_name):
        if obj is None:
            return ''

        if '__' in attribute_name:
            (a1, a2) = attribute_name.split('__', 1)
            try:
                o = getattr(obj, a1)
            except AttributeError:
                o = None
            return extended_getattr(o, a2)
        else:
            try:
                return getattr(obj, attribute_name)
            except AttributeError:
                return ''


    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        standard_field_names = [field.name for field in opts.fields]
        labels = []
        if exclude:
            field_names = [v for v in standard_field_names if v not in exclude]
        elif fields:
            field_names = [k for k, v in fields if k in standard_field_names or '__' in k]
            labels = [v for k, v in fields if k in standard_field_names or '__' in k]
        else:
            field_names = standard_field_names

        # uncomment this if download is not required required
        # response = HttpResponse(mimetype='text/plain; charset=utf8')

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = csv.writer(response, delimiter=';')
        if header:
            if labels:
                writer.writerow(labels)
            else:
                writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([unicode(extended_getattr(obj, field)).encode('utf-8') for field in field_names])
        return response


    export_as_csv.short_description = description
    return export_as_csv


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
        export_select_fields_csv_action("Esporta i selezionati in formato CSV",
             fields=[
                 ('contact__first_name', 'Nome'),
                 ('contact__last_name', 'Cognome'),
                 ('contact__email', 'Email'),
                 ('title', 'Qualifica'),
                 ('role', 'Ruolo'),
                 ('user_type', 'Tipo utente'),
                 ('notes', 'Note'),
                 ('source__name', 'Fonte')
             ],
             header=True
        ),
    ]


admin.site.register(Fonte, SourceAdmin)
admin.site.register(Contatto, ContactAdmin)
admin.site.register(Iscrizione, SubscriptionAdmin)