from django.db import models
from django.utils.translation import ugettext_lazy as _


class Dish(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=300)


class Canteen(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=100)


class Serving(models.Model):
    date = models.DateField()
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE)
