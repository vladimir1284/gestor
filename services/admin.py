from django.contrib import admin

from .models import (
    ServiceCategory,
    Service,
    ServiceTransaction,
    ServicePicture,
    Payment,
    PaymentCategory,
    PendingPayment,
    DebtStatus,
)


admin.site.register(Service)
admin.site.register(ServiceTransaction)
admin.site.register(ServiceCategory)
admin.site.register(ServicePicture)
admin.site.register(Payment)
admin.site.register(PaymentCategory)
admin.site.register(PendingPayment)
admin.site.register(DebtStatus)
