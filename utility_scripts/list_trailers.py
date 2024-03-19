from rent.models.vehicle import Trailer
from utils.models import Order

trailers = Trailer.objects.all().order_by('id')

print("VIN,First order,Active")
for trailer in trailers:
    first_order = Order.objects.filter(
        trailer=trailer).order_by('created_date').first()
    if first_order:
        print(f"{trailer.vin}, {first_order.created_date.date()}, {trailer.active}")
    else:
        print(f"{trailer.vin}, No orders, {trailer.active}")
