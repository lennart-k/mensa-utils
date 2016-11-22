from django.core.management import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from mensautils.base.mensa import fetch_mensa


class Command(BaseCommand):
    help = 'Fetch the mensa data.'

    def handle(self, *args, **options):
        """Update the cache."""
        rendered = render_to_string(
            'mensautils/mensa.html', {
                'mensa_data': fetch_mensa().items(),
                'last_refresh': timezone.now(),
            })
        print(rendered)
