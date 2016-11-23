from datetime import datetime

from decimal import Decimal

from mensautils.canteen.models import Canteen, Dish, Serving


def store_canteen_data(day: datetime.date, canteen_name: str, dishes: dict):
    """Save or update the canteen data by a canteen data objects returned from
    fetch_mensa."""
    canteen, _ = Canteen.objects.get_or_create(name=canteen_name)
    for dish_data in dishes:
        # todo: merge same dishes with different names
        dish, _ = Dish.objects.get_or_create(
            name=dish_data['title'], vegetarian=dish_data['vegetarian'])

        price = Decimal(dish_data['price'].replace(',', '.'))
        price_staff = Decimal(dish_data['price_staff'].replace(',', '.'))

        # add serving
        Serving.objects.get_or_create(
            date=day, canteen=canteen, dish=dish, price=price,
            price_staff=price_staff)
