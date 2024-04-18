from utils.models import Order

orders = Order.objects.filter(status="complete")

for order in orders:
    if order.position:
        print(order.id)
        order.position = None
        order.save()
