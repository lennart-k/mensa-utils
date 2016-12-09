from django.utils import timezone

from mensautils.canteen.models import Canteen, Dish, Serving
from mensautils.parser.canteen_result import CanteenResult


def store_canteen_data(canteen_name: str, result: CanteenResult):
    """Save/update the canteen data and a CanteenResult returned by parser."""
    canteen, _ = Canteen.objects.get_or_create(name=canteen_name)

    now = timezone.now()

    for serving in result.servings:
        dish = Dish.fuzzy_find_or_create(
            name=serving.title, vegetarian=serving.vegetarian)

        # search for serving (allow different price)
        possible_servings = Serving.objects.filter(
            date=serving.day, canteen=canteen, dish=dish)
        if possible_servings.count() == 0:
            # create new entry
            created = True
            serving_object = Serving.objects.create(
                date=serving.day, canteen=canteen, dish=dish,
                price=serving.price, price_staff=serving.price_staff)
        elif possible_servings.count() == 1:
            created = False
            serving_object = possible_servings.first()
            serving_object.price = serving.price
            serving_object.price_staff = serving.price_staff
        else:
            # multiple servings. filter for price.
            created = False
            # TODO: missing handling of this case

        if not created:
            serving_object.last_updated = now
            serving_object.officially_deprecated = False
            serving_object.official = True
            serving_object.save()

    # mark old dishes for same day and canteen as deprecated
    Serving.objects.filter(
        date=serving.day, canteen=canteen, last_updated__lt=now, official=True
    ).update(officially_deprecated=True)
