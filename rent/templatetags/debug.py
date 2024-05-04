from django import template

register = template.Library()


@register.simple_tag
def msg(*args):
    print(*args)
