from django.contrib import admin

# Register your models here.
from .models import Order, Statistics, Plate, MonthlyStatistics, OrderTrace

admin.site.register(Order)
admin.site.register(Statistics)
admin.site.register(MonthlyStatistics)
admin.site.register(Plate)
admin.site.register(OrderTrace)
