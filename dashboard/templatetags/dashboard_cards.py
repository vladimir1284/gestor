from django import template
from django.http import HttpRequest

from dashboard.dashboard.dashboard_card import DashboardCard


register = template.Library()


@register.simple_tag
def renderDBC(card: DashboardCard, request: HttpRequest):
    return card.render(request)
