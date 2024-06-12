from django.contrib import admin

from .models import DebtStatus
from .models import Payment
from .models import PaymentCategory
from .models import PendingPayment
from .models import Service
from .models import ServiceCategory
from .models import ServicePicture
from .models import ServiceTransaction
from services.models.order_signature import OrderSignature
from services.models.preorder import Preorder

admin.site.register(Service)
admin.site.register(ServiceTransaction)
admin.site.register(ServiceCategory)
admin.site.register(ServicePicture)
admin.site.register(Payment)
admin.site.register(PaymentCategory)
admin.site.register(PendingPayment)
admin.site.register(DebtStatus)
admin.site.register(Preorder)
admin.site.register(OrderSignature)
