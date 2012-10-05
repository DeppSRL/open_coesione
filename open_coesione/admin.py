from django.contrib import admin
from open_coesione.models import ContactMessage, PressReview

class MessagesAdmin(admin.ModelAdmin):
    date_hierarchy = 'sent_at'
    list_display = ('sender', 'email', 'organization', 'sent_at')

class PressReviewAdmin(admin.ModelAdmin):
    date_hierarchy = 'published_at'
    list_display = ('title', 'source', 'author', 'published_at')

admin.site.register(ContactMessage, MessagesAdmin)
admin.site.register(PressReview, PressReviewAdmin)



