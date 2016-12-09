from django.conf import settings
from django.core.management import BaseCommand

from mensautils.canteen.archive import store_canteen_data
from mensautils.canteen.notifications import send_notifications


class Command(BaseCommand):
    help = 'Fetch the canteen data.'

    def handle(self, *args, **options):
        """Update the cache."""
        for canteen_name, canteen_callable, canteen_kwargs in settings.CANTEENS:
            canteen_result = canteen_callable(**canteen_kwargs)
            store_canteen_data(
                canteen_name, canteen_result)

        # send notifications for today
        send_notifications()
