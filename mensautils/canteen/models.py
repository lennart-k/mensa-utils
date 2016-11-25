from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, Count
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
            if fuzz.token_sort_ratio(name, dish.name) >= settings.FUZZY_MIN_RATIO:
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
    officially_deprecated = models.BooleanField(default=False)

    def __str__(self):
        return '{}: {} ({}, {})'.format(self.canteen, str(self.dish), str(self.date),
                                        self.price)

    def average_rating(self) -> float:
        """Get average rating."""
        if hasattr(self, 'ratings__rating__avg'):
            return self.ratings__rating__avg
        return self.ratings.aggregate(Avg('rating'))['rating__avg']

    def rating_count(self) -> int:
        """Get rating count."""
        if hasattr(self, 'ratings__count'):
            return self.ratings__count
        return self.ratings.count()

    def deprecation_reports_count(self):
        if hasattr(self, 'deprecation_reports__count'):
            return self.deprecation_reports__count
        else:
            return self.aggregate(
                Count('deprecation_reports'))['deprecation_reports__count']

    @property
    def deprecated(self) -> bool:
        return (self.officially_deprecated or
                self.deprecation_reports_count() >= settings.MIN_REPORTS)

    @property
    def maybe_deprecated(self) -> bool:
        """Maybe deprecated when at least one user has reported serving."""
        reports = self.deprecation_reports_count()
        return reports >= 1


class Rating(models.Model):
    class Meta:
        unique_together = [('user', 'serving')]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    serving = models.ForeignKey(
        Serving, on_delete=models.CASCADE, related_name='ratings')
    rating = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return '{}: {} ({})'.format(self.rating, str(self.serving), self.user)


class InofficialDeprecation(models.Model):
    """Deprecation reported by users."""
    class Meta:
        unique_together = [('serving', 'reporter')]
    serving = models.ForeignKey(
        Serving, on_delete=models.CASCADE, related_name='deprecation_reports')
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='deprecation_reports')

    def __str__(self):
        return '{}: {}'.format(self.reporter, self.serving)
