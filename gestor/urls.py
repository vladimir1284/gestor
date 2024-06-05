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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path

from .views import cost
from .views import dashboard
from .views import reports
from gestor.tools.emails_domains import init_temp_emails_domains
from gestor.tools.week_stats_recal import initRecalculator
from gestor.views.emails_domains import emails_domains
from rbac.init_permissions import init_permissions


def trigger_error(request):
    pass


initRecalculator()


urlpatterns = [
    path("erp/sentry-debug/", trigger_error),
    path("erp/admin/", admin.site.urls),
    path("erp/", dashboard.dashboard, name="dashboard"),
    # Weekly reports
    path("erp/weekly/", reports.weekly_report, name="weekly-report"),
    path("erp/weekly/<date>", reports.weekly_report, name="weekly-report-date"),
    path(
        "erp/weekly/<category_id>/<date>",
        reports.weekly_payments,
        name="weekly-payments",
    ),
    path(
        "erp/weekly_membership/",
        reports.weekly_membership_report,
        name="weekly-membership",
    ),
    path(
        "erp/weekly_membership/<date>",
        reports.weekly_membership_report,
        name="weekly-membership-date",
    ),
    path(
        "erp/week-stats-recalculate/<date>",
        dashboard.week_stats_recalculate,
        name="week-stats-recalculate",
    ),
    path("erp/weekly-costs/<category_id>/<date>", cost.weekly_cost, name="weekly-cost"),
    # Monthly reports
    path("erp/monthly/", reports.monthly_report, name="monthly-report"),
    path(
        "erp/monthly/<year>/<month>", reports.monthly_report, name="monthly-report-date"
    ),
    path(
        "erp/monthly/<category_id>/<year>/<month>",
        reports.monthly_payments,
        name="monthly-payments",
    ),
    path(
        "erp/monthly_membership/",
        reports.monthly_membership_report,
        name="monthly-membership",
    ),
    path(
        "erp/monthly_membership/<year>/<month>",
        reports.monthly_membership_report,
        name="monthly-membership-date",
    ),
    path(
        "erp/monthly-costs/<category_id>/<year>/<month>",
        cost.monthly_cost,
        name="monthly-cost",
    ),
    # Tools
    path("erp/emails_domains", emails_domains, name="emails_domains"),
    # Apps
    path("erp/users/", include("users.urls")),
    path("erp/inventory/", include("inventory.urls")),
    path("erp/services/", include("services.urls")),
    path("erp/equipment/", include("equipment.urls")),
    path("erp/costs/", include("costs.urls")),
    path("erp/rent/", include("rent.urls")),
    path("erp/utils/", include("utils.urls")),
    path("erp/tolls/", include("tolls.urls")),
    path("erp/template/", include("template_admin.urls")),
    path("erp/rbac/", include("rbac.urls")),
    path("erp/crm/", include("crm.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


init_permissions()

try:
    init_temp_emails_domains()
except Exception as e:
    print(e)
