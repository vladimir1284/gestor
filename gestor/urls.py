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

from .views import dashboard, report, weekly_report, weekly_membership_report

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('report/<year>/<month>', report, name='report'),
    path('weekly/', weekly_report, name='weekly-report'),
    path('weekly/<date>', weekly_report, name='weekly-report-date'),
    path('weekly_membership/', weekly_membership_report, name='weekly-membership'),
    path('weekly_membership/<date>', weekly_membership_report,
         name='weekly-membership-date'),
    path('users/', include('users.urls')),
    path('inventory/', include('inventory.urls')),
    path('services/', include('services.urls')),
    path('equipment/', include('equipment.urls')),
    path('costs/', include('costs.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
