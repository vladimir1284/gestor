from django.contrib import admin

from .models import User, UserProfile


class UserAdmin(admin.ModelAdmin):
    list_display = ['username']

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
