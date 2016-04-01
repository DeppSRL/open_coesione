# -*- coding: utf-8 -*-
from django.contrib import admin
from models import URL


class URLAdmin(admin.ModelAdmin):
    list_display = ('url', 'short_url', 'visit_count')
    fields = ('url',)

    def short_url(self, obj):
        from django.conf import settings
        from django.utils.html import format_html
        return format_html('<a href="{0}" target="_blank">{0}</a>', 'http://{}{}'.format(settings.URLSHORTENER_DOMAIN, obj.get_absolute_url()))
    short_url.short_description = 'URL breve'

admin.site.register(URL, URLAdmin)
