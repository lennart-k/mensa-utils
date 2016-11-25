from django import template
from math import floor

from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def stars(value: float) -> str:
    result = ''
    floored = floor(value)
    remainder = value - floored
    for _ in range(floored):
        result += '&#x2605;'
    if remainder > 0:
        result += '<span style="opacity: {};">&#x2605;</span>'.format(remainder)
    result = '<span title="{}/5">{}</span>'.format(value, result)
    return mark_safe(result)
