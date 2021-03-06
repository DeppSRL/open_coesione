# -*- coding: utf-8 -*-
from django.contrib.gis import admin
from models import Entry
from django.forms import ModelForm, CharField
from tinymce.widgets import TinyMCE
from tagging.admin import TagInline


class BlogEntryAdminForm(ModelForm):
    body = CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 10}))

    class Meta:
        model = Entry


class BlogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'published_at'
    list_display = ('title', 'published_at')
    exclude = ['body_plain']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TagInline]
    form = BlogEntryAdminForm


admin.site.register(Entry, BlogEntryAdmin)
