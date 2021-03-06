# -*- coding: utf-8 -*-
from django.contrib import admin
from tagging.models import *


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority')
    list_editable = ('priority',)


class TagInline(generic.GenericTabularInline):
    model = TaggedItem
    extra = 0


admin.site.register(Tag, TagAdmin)
