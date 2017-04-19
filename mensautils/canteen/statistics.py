from django.db.models import Count, Avg

from mensautils.canteen.models import Dish


def get_most_frequent_dishes():
    dishes = Dish.objects.annotate(
        servings__count=Count('servings')).order_by(
        '-servings__count')[:10]
    return dishes


def get_most_favored_dishes():
    dishes = Dish.objects.annotate(
        servings__ratings__rating__count=Count('servings__ratings__rating'),
        servings__ratings__rating__avg=Avg('servings__ratings__rating')).filter(
        servings__ratings__rating__avg__isnull=False).order_by(
        '-servings__ratings__rating__avg')[:10]
    return dishes
