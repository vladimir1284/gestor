from django.contrib import admin

from .models import (
    ServiceCategory,
    Service,
    ServicePicture,
    Payment,
    PaymentCategory,
    PendingPayment
)


admin.site.register(Service)
admin.site.register(ServiceCategory)
admin.site.register(ServicePicture)
admin.site.register(Payment)
admin.site.register(PaymentCategory)
admin.site.register(PendingPayment)
