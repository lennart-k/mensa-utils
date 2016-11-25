from datetime import datetime

from decimal import Decimal

from django.utils import timezone

from mensautils.canteen.models import Canteen, Dish, Serving


def store_canteen_data(day: datetime.date, canteen_name: str, dishes: dict):
    """Save or update the canteen data by a canteen data objects returned from
    fetch_mensa."""
    canteen, _ = Canteen.objects.get_or_create(name=canteen_name)

    now = timezone.now()

    for dish_data in dishes:
        dish = Dish.fuzzy_find_or_create(
            name=dish_data['title'], vegetarian=dish_data['vegetarian'])

        price = Decimal(dish_data['price'].replace(',', '.'))
        price_staff = Decimal(dish_data['price_staff'].replace(',', '.'))

        # add serving
        serving, created = Serving.objects.get_or_create(
            date=day, canteen=canteen, dish=dish, price=price,
            price_staff=price_staff)
        if not created:
            serving.last_updated = now
            serving.deprecated = False
            serving.official = True
            serving.save()

    # mark old dishes for same day and canteen as deprecated
    Serving.objects.filter(
        date=day, canteen=canteen, last_updated__lt=now, official=True).update(
        deprecated=True)
