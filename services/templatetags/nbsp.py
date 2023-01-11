# templatetags/nbsp.py

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def nbsp(value):
    ms = mark_safe("&nbsp;".join(str(value).split(' ')))
    ms = mark_safe("&#8209;".join(ms.split('-')))
    return ms
