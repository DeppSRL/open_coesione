from django.contrib import admin
from open_coesione.models import ContactMessage, PressReview, Pillola

from tagging.admin import TagInline

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
    inlines = [TagInline]

admin.site.register(ContactMessage, MessagesAdmin)
admin.site.register(PressReview, PressReviewAdmin)
admin.site.register(Pillola, PillolaAdmin)
