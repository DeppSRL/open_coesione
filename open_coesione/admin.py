from django.contrib import admin
from open_coesione.models import ContactMessage

class MessagesAdmin(admin.ModelAdmin):
    date_hierarchy = 'sent_at'
    list_display = ('sender', 'email', 'organization', 'sent_at')

admin.site.register(ContactMessage, MessagesAdmin)


