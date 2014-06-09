from django.contrib import admin
from tagging.models import *
from django.forms import ModelForm

class TagInline(generic.GenericTabularInline):
    model = TaggedItem
    extra = 0

class TagForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Termine'

class TagAdmin(admin.ModelAdmin):
    form = TagForm

admin.site.register(Tag, TagAdmin)
