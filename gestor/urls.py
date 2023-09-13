"""inventory URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    dashboard,
    # report,
    weekly_report,
    weekly_membership_report,
    monthly_report,
    monthly_membership_report,
    weekly_payments,
    monthly_payments,
    week_stats_recalculate,
    weekly_cost,
    monthly_cost
)

urlpatterns = [
    path('erp/admin/', admin.site.urls),
    path('erp/', dashboard, name='dashboard'),
    # Weekly reports
    path('erp/weekly/', weekly_report, name='weekly-report'),
    path('erp/weekly/<date>', weekly_report, name='weekly-report-date'),
    path('erp/weekly/<category_id>/<date>',
         weekly_payments, name='weekly-payments'),
    path('erp/weekly_membership/', weekly_membership_report,
         name='weekly-membership'),
    path('erp/weekly_membership/<date>', weekly_membership_report,
         name='weekly-membership-date'),
    path('erp/week-stats-recalculate/<date>',
         week_stats_recalculate, name='week-stats-recalculate'),
    path('erp/weekly-costs/<category_id>/<date>',
         weekly_cost, name='weekly-cost'),

    # Monthly reports
    path('erp/monthly/', monthly_report, name='monthly-report'),
    path('erp/monthly/<year>/<month>',
         monthly_report, name='monthly-report-date'),
    path('erp/monthly/<category_id>/<year>/<month>',
         monthly_payments, name='monthly-payments'),
    path('erp/monthly_membership/', monthly_membership_report,
         name='monthly-membership'),
    path('erp/monthly_membership/<year>/<month>', monthly_membership_report,
         name='monthly-membership-date'),
    path('erp/monthly-costs/<category_id>/<year>/<month>', monthly_cost,
         name='monthly-cost'),

    # Apps
    path('erp/users/', include('users.urls')),
    path('erp/inventory/', include('inventory.urls')),
    path('erp/services/', include('services.urls')),
    path('erp/equipment/', include('equipment.urls')),
    path('erp/costs/', include('costs.urls')),
    path('erp/rent/', include('rent.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
