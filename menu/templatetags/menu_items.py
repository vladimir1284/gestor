from django import template
from django.http import HttpRequest

from menu.menu.menu_element import MenuItem

register = template.Library()


@register.simple_tag
def renderMI(menu_item: MenuItem, request: HttpRequest):
    return menu_item.render(request)


@register.simple_tag
def activeMI(
    menu_item: MenuItem,
    request: HttpRequest,
    recursive: bool = False,
) -> bool:
    return menu_item.is_active(request, recursive)


@register.simple_tag
def miOpenClass(
    menu_item: MenuItem,
    request: HttpRequest,
) -> str:
    if menu_item.is_active(request, True):
        return "open"
    return ""


@register.simple_tag
def miActiveClass(
    menu_item: MenuItem,
    request: HttpRequest,
) -> str:
    if menu_item.is_active(request, True):
        return "active"
    return ""
