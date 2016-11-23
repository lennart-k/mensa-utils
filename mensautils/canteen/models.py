from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from fuzzywuzzy import fuzz


class Dish(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=300)
    vegetarian = models.BooleanField()

    def __str__(self):
        return self.name

    @staticmethod
    def fuzzy_find_or_create(name: str, vegetarian: bool) -> 'Dish':
        for dish in Dish.objects.filter(vegetarian=vegetarian):
            if fuzz.partial_ratio(name, dish.name) >= settings.FUZZY_MIN_RATIO:
                return dish
        return Dish.objects.create(name=name, vegetarian=vegetarian)


class Canteen(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=100)

    def __str__(self):
        return self.name


class Serving(models.Model):
    date = models.DateField()
    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE, related_name='servings')
    canteen = models.ForeignKey(
        Canteen, on_delete=models.CASCADE, related_name='servings')
    price = models.DecimalField(max_digits=4, decimal_places=2)
    price_staff = models.DecimalField(max_digits=4, decimal_places=2)

    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '{}: {} ({}, {})'.format(self.canteen, str(self.dish), str(self.date),
                                        self.price)
