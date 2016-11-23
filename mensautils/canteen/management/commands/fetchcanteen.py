from datetime import date
from datetime import timedelta

from django.conf import settings
from django.core.management import BaseCommand

from mensautils.canteen.archive import store_canteen_data
from mensautils.canteen.canteen import fetch_canteen


class Command(BaseCommand):
    help = 'Fetch the canteen data.'

    def handle(self, *args, **options):
        """Update the cache."""
        today = date.today()

        for day in (today, today + timedelta(days=1)):
            for canteen_name, canteen_url in settings.CANTEENS:
                canteen_data = fetch_canteen(day, canteen_url)
                store_canteen_data(
                    day, canteen_name, canteen_data)
                store_canteen_data(
                    day, canteen_name, canteen_data)
