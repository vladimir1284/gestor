from django.contrib import admin

# Register your models here.
from .models import Order, Statistics, Plate

admin.site.register(Order)
admin.site.register(Statistics)
admin.site.register(Plate)
