from django.contrib import admin
from .models import User
from .models import UserSessionLog
from django.utils.timezone import localtime

@admin.register(User)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'u_name',
        'email',
        'role',
    )
@admin.register(UserSessionLog)
class UserSessionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time_ist', 'logout_time_ist')

    def login_time_ist(self, obj):
        return localtime(obj.login_time).strftime('%b %d, %Y, %I:%M %p')

    def logout_time_ist(self, obj):
        if obj.logout_time:
            return localtime(obj.logout_time).strftime('%b %d, %Y, %I:%M %p')
        return '-'

    login_time_ist.short_description = 'Login Time (IST)'
    logout_time_ist.short_description = 'Logout Time (IST)'