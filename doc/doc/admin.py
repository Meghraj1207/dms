
from django.contrib import admin
from documents.models import Document
from django.contrib.auth import get_user_model

User = get_user_model()
admin.site.register(User)
admin.site.register(Document)

from django.contrib import admin
from auditlog.models import LogEntry

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        'object_repr',
        'content_type',
        'action',
        'timestamp',
        'actor',
        'changes'
    )
    list_filter = ('content_type', 'action', 'actor')
    search_fields = ('object_repr', 'changes', 'actor__username')
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False