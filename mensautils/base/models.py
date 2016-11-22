from django.db import models
from django.utils.translation import ugettext_lazy as _


class Dish(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=300)

    def __str__(self):
        return self.name


class Canteen(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=100)

    def __str__(self):
        return self.name


class Serving(models.Model):
    date = models.DateField()
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return '{}: {} ({}, {})'.format(self.canteen, str(self.dish), str(self.date),
                                        self.price)
