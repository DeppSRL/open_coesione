from django.contrib import admin
from models import ContactMessage, PressReview, Pillola, URL
from django.forms import ModelForm, CharField
from django.contrib.contenttypes import generic

from tinymce.widgets import TinyMCE

from tagging.admin import TagInline

class PillolaAdminForm(ModelForm):
    description = CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 10}))
    class Meta:
        model = Pillola

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

class URLInline(generic.GenericTabularInline):
    model = URL
    extra = 0

admin.site.register(ContactMessage, MessagesAdmin)
admin.site.register(PressReview, PressReviewAdmin)
admin.site.register(Pillola, PillolaAdmin)
