from django.db.models import Q

from utils.models import Order


orders = Order.objects.filter(
    ~Q(type="sell"),
    quotation=True,
)
for o in orders:
    o.type = "sell"
    o.save()
