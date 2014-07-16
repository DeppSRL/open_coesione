from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from models import ContactMessage, PressReview, Pillola, URL, FAQ
from django.forms import ModelForm, CharField
from django.contrib.contenttypes import generic

from tinymce.widgets import TinyMCE

from tagging.admin import TagInline


from django.contrib.flatpages.admin import FlatPageAdmin, FlatpageForm


common_mce_attrs = {
    'theme': "advanced",
    'plugins': "fullscreen,media,preview,advimage,table",
    'plugin_preview_width' : "1280",
    'plugin_preview_height' : "800",
    'content_css' : "/static/css/bootstrap.css",
    'plugin_preview_pageurl': "/tinymce/preview/content",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    'height': 500,
    'theme_advanced_buttons1' : "bold,italic,underline,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,|,outdent,indent,|,formatselect,|,undo,redo",
    'theme_advanced_buttons2' : "link,unlink,|,image,media,|,tablecontrols,fullscreen,zoom,|,preview,code",
    'theme_advanced_buttons3': "",
    'theme_advanced_toolbar_location': "top"
}


class TinyMCEEnabledForm(ModelForm):
    class Media:
        js = [
            '/static/tiny_mce/tiny_mce.js',
        ]

    pass


class OCFlatpageForm(TinyMCEEnabledForm, FlatpageForm):
    common_mce_attrs['plugin_preview_pageurl'] = "/tinymce/preview/page"

    content = CharField(widget=TinyMCE(
        mce_attrs=common_mce_attrs
    ))

class OCFlatPageAdmin(FlatPageAdmin):
    form = OCFlatpageForm

class PillolaAdminForm(TinyMCEEnabledForm):
    description = CharField(widget=TinyMCE(mce_attrs=common_mce_attrs))
    class Meta:
        model = Pillola

class FAQAdminForm(TinyMCEEnabledForm):
    risposta_it = CharField(widget=TinyMCE(mce_attrs=common_mce_attrs))
    risposta_en = CharField(widget=TinyMCE(mce_attrs=common_mce_attrs))
    class Meta:
        model = FAQ

class MessagesAdmin(admin.ModelAdmin):
    date_hierarchy = 'sent_at'
    list_display = ('sender', 'email', 'organization', 'sent_at')

class PressReviewAdmin(admin.ModelAdmin):
    date_hierarchy = 'published_at'
    list_display = ('title', 'source', 'author', 'published_at')

class PillolaAdmin(admin.ModelAdmin):
    date_hierarchy = 'published_at'
    list_display = ('title', 'file', 'published_at')
    ordering = ('-published_at',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TagInline]
    form = PillolaAdminForm

class FAQAdmin(admin.ModelAdmin):
    list_display = ('domanda_it', 'domanda_en')
    prepopulated_fields = {'slug_it': ('domanda_it',), 'slug_en': ('domanda_en',)}
    form = FAQAdminForm

class URLInline(generic.GenericTabularInline):
    model = URL
    extra = 0

admin.site.register(ContactMessage, MessagesAdmin)
admin.site.register(PressReview, PressReviewAdmin)
admin.site.register(Pillola, PillolaAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, OCFlatPageAdmin)
