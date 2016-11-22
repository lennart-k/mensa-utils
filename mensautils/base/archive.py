from datetime import datetime

from mensautils.base.models import Canteen, Dish, Serving


def store_canteen_data(canteen_data: dict):
    """Save or update the canteen data by a canteen data objects returned from
    fetch_mensa."""
    for canteen_name, dishes in canteen_data:
        canteen, _ = Canteen.objects.get_or_create(name=canteen_name)
        for dish_description in dishes:
            # todo: merge same dishes with different names
            dish, _ = Dish.objects.get_or_create(name=dish_description['title'])

            # add serving
            Serving.objects.get_or_create(
                date=datetime.today(), canteen=canteen, dish=dish)
