from django.contrib import admin

from .models import (
    ServiceCategory,
    Service,
    ServicePicture
)


admin.site.register(Service)
admin.site.register(ServiceCategory)
admin.site.register(ServicePicture)
