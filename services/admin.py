from django.contrib import admin

from .models import (
    ServiceCategory,
    Service,
)


admin.site.register(Service)
admin.site.register(ServiceCategory)
