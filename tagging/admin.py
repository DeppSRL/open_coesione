from django.contrib import admin
from tagging.models import *

class TagInline(generic.GenericTabularInline):
    model = TaggedItem
    extra = 0

admin.site.register(Tag)
