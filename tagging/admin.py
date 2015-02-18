from django.contrib import admin
from tagging.models import *


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority')


class TagInline(generic.GenericTabularInline):
    model = TaggedItem
    extra = 0


admin.site.register(Tag, TagAdmin)
