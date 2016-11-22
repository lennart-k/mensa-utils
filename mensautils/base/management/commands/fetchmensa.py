from django.core.management import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from mensautils.base.archive import store_canteen_data
from mensautils.base.mensa import fetch_mensa


class Command(BaseCommand):
    help = 'Fetch the mensa data.'

    def handle(self, *args, **options):
        """Update the cache."""
        mensa_data = fetch_mensa()
        rendered = render_to_string(
            'mensautils/mensa.html', {
                'mensa_data': mensa_data.items(),
                'last_refresh': timezone.now(),
            })
        # store canteen data for current day (not for next)
        store_canteen_data(mensa_data[0][1])
        print(rendered)
