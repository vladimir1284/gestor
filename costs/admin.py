from django.contrib import admin

from .models import CostCategory, Cost

admin.site.register(Cost)
admin.site.register(CostCategory)
