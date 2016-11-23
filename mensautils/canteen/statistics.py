from django.db.models import Count

from mensautils.canteen.models import Dish


def get_most_frequent_dishes():
    dishes = Dish.objects.annotate(
        servings__count=Count('servings')).order_by(
        '-servings__count')[:10]
    return dishes
