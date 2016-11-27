from datetime import date
from datetime import timedelta

from django.conf import settings
from django.core.management import BaseCommand

from mensautils.canteen.archive import store_canteen_data
from mensautils.canteen.canteen import fetch_canteen
from mensautils.canteen.notifications import send_notifications


class Command(BaseCommand):
    help = 'Fetch the canteen data.'

    def handle(self, *args, **options):
        """Update the cache."""
        days = [0, 99]

        for day in days:
            for canteen_name, canteen_url in settings.CANTEENS:
                canteen_date, canteen_foods = fetch_canteen(day, canteen_url)
                store_canteen_data(
                    canteen_date, canteen_name, canteen_foods)

        # send notifications for today
        send_notifications()
