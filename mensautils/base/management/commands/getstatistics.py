from django.core.management import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from mensautils.base.statistics import get_most_frequent_dishes


class Command(BaseCommand):
    help = 'Calculate some fancy statistics to html.'

    def handle(self, *args, **options):
        """Calculate statistics."""
        most_frequent_dishes = get_most_frequent_dishes()
        rendered = render_to_string(
            'mensautils/statistics.html', {
                'most_frequent_dishes': most_frequent_dishes,
                'last_refresh': timezone.now(),
            })
        print(rendered)
