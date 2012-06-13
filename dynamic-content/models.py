from django.contrib.markup.templatetags.markup import textile
from django.utils.translation import ugettext_lazy as _
from django.db import models

from feincms.module.page.models import Page
from feincms.content.richtext.models import RichTextContent
from feincms.content.medialibrary.v2 import MediaFileContent

Page.register_extensions('changedate', 'datepublisher', 'seo')

Page.register_templates({
    'title': _('Standard template'),
    'path': 'dynamic-page.html',
    'regions': (
        ('main', _('Main content area')),
        ('sidebar', _('Sidebar'), 'inherited'),
        ),
    })

Page.create_content_type(RichTextContent)
Page.create_content_type(MediaFileContent, TYPE_CHOICES=(
    ('default', _('default')),
    ('lightbox', _('lightbox')),
))


# Textile content for page (test)
class TextilePageContent(models.Model):
    content = models.TextField()

    class Meta:
        abstract = True

    def render(self, **kwargs):
        return textile(self.content)

Page.create_content_type(TextilePageContent)