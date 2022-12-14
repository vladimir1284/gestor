from django.contrib import admin

from .models import (
    User,
    UserProfile,
    Associated,
    Company,
)


class UserAdmin(admin.ModelAdmin):
    list_display = ['username']


admin.site.unregister(User)
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Associated)
admin.site.register(Company)
