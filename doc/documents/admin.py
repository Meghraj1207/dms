from django.contrib import admin
from .models import Document
from django.utils.timezone import localtime

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'uploaded_by', 'status', 'get_uploaded_at', 'get_reviewed_at', 'get_approved_at')

    def get_uploaded_at(self, obj):
        return localtime(obj.uploaded_at).strftime('%b %d, %Y, %I:%M %p')
    get_uploaded_at.short_description = 'Uploaded At (IST)'

    def get_reviewed_at(self, obj):
        if obj.reviewed_at:
            return localtime(obj.reviewed_at).strftime('%b %d, %Y, %I:%M %p')
    get_reviewed_at.short_description = 'Reviewed At (IST)'

    def get_approved_at(self, obj):
        if obj.approved_at:
            return localtime(obj.approved_at).strftime('%b %d, %Y, %I:%M %p')
    get_approved_at.short_description = 'Approved At (IST)'