from django.contrib import admin

# Register your models here.
from .models import Order, Statistics

admin.site.register(Order)
admin.site.register(Statistics)
