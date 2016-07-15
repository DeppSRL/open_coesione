# coding=utf-8
from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from models import ContactMessage, PressReview, Pillola, File, Link, FAQ
from django.forms import ModelForm
from django.contrib.contenttypes import generic

from tinymce.widgets import TinyMCE
from open_coesione.utils import export_select_fields_csv_action

from tagging.admin import TagInline


from django.contrib.flatpages.admin import FlatPageAdmin, FlatpageForm


common_mce_attrs = {
    'theme': 'advanced',
    'plugins': 'fullscreen,media,preview,advimage,table',
    'plugin_preview_width': '1280',
    'plugin_preview_height': '800',
    'content_css': '/static/css/bootstrap.css',
    'plugin_preview_pageurl': '/tinymce/preview/content',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    'height': 500,
    'theme_advanced_buttons1': 'bold,italic,underline,removeformat,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,|,outdent,indent,|,formatselect,|,undo,redo',
    'theme_advanced_buttons2': 'link,unlink,|,image,media,|,tablecontrols,fullscreen,zoom,|,preview,code',
    'theme_advanced_buttons3': '',
    'theme_advanced_toolbar_location': 'top'
}


class TinyMCEEnabledForm(ModelForm):
    class Media:
        js = [
            '/static/tiny_mce/tiny_mce.js',
        ]


class OCFlatpageForm(TinyMCEEnabledForm, FlatpageForm):
    class Meta(FlatpageForm.Meta):
        common_mce_attrs['plugin_preview_pageurl'] = '/tinymce/preview/page'
        widgets = {
            'content': TinyMCE(mce_attrs=common_mce_attrs),
            'extra_content': TinyMCE(mce_attrs=common_mce_attrs),
        }


class PillolaAdminForm(TinyMCEEnabledForm):
    class Meta:
        widgets = {
            'abstract': TinyMCE(mce_attrs=common_mce_attrs),
            'description': TinyMCE(mce_attrs=common_mce_attrs)
        }


class FAQAdminForm(TinyMCEEnabledForm):
    class Meta:
        widgets = {
            'risposta_it': TinyMCE(mce_attrs=common_mce_attrs),
            'risposta_en': TinyMCE(mce_attrs=common_mce_attrs)
        }


class FileInline(generic.GenericTabularInline):
    model = File
    verbose_name = 'Documento'
    verbose_name_plural = 'Documenti'
    extra = 0


class LinkInline(generic.GenericTabularInline):
    model = Link
    verbose_name = 'Collegamento'
    verbose_name_plural = 'Collegamenti'
    extra = 0


class OCFlatPageAdmin(FlatPageAdmin):
    form = OCFlatpageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'extra_content', 'sites')}),
    )


class MessagesAdmin(admin.ModelAdmin):
    date_hierarchy = 'sent_at'
    list_display = ('sender', 'email', 'organization', 'sent_at')
    actions = [
        export_select_fields_csv_action(
            'Esporta i selezionati in formato CSV',
            fields=[
                ('sender', 'Nome'),
                ('email', 'E-mail'),
                ('organization', 'Organizzazione'),
                ('location', u'Località'),
                ('reason', 'Motivo'),
                ('body', 'Messaggio'),
                ('sent_at', 'Qualifica'),
            ],
            header=True
        ),
    ]


class PressReviewAdmin(admin.ModelAdmin):
    date_hierarchy = 'published_at'
    list_display = ('title', 'source', 'author', 'published_at')


class PillolaAdmin(admin.ModelAdmin):
    date_hierarchy = 'published_at'
    list_display = ('title', 'published_at', 'in_english')
    ordering = ('-published_at',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [FileInline, TagInline]
    form = PillolaAdminForm


class FAQAdmin(admin.ModelAdmin):
    list_display = ('domanda_it', 'domanda_en', 'priorita')
    list_editable = ('priorita',)
    prepopulated_fields = {'slug_it': ('domanda_it',), 'slug_en': ('domanda_en',)}
    form = FAQAdminForm


admin.site.register(ContactMessage, MessagesAdmin)
admin.site.register(PressReview, PressReviewAdmin)
admin.site.register(Pillola, PillolaAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, OCFlatPageAdmin)
