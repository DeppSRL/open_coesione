from django.contrib.gis import admin
from models import Entry
from django.forms import ModelForm, CharField

from tinymce.widgets import TinyMCE

class BlogEntryForm(ModelForm):
    body = CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 10}))
    class Meta:
        model = Entry


class BlogEntryAdmin(admin.ModelAdmin):
    date_hierarchy= 'published_at'
    exclude = ['body_plain']
    form = BlogEntryForm

admin.site.register(Entry, BlogEntryAdmin)
