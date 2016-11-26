from datetime import date, timedelta
from django import template
from math import floor

from django.template.defaultfilters import date as django_date
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def day_description(value: date) -> str:
    today = date.today()
    if value == today:
        return 'Heute ({})'.format(django_date(value, 'l'))
    tomorrow = today + timedelta(days=1)
    if value == tomorrow:
        return 'Morgen ({})'.format(django_date(value, 'l'))
    return django_date(value, 'l')
