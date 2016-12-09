from datetime import date, time
from decimal import Decimal
from typing import Dict, List, Set, Tuple


class Serving:
    day = None
    title = None
    price = None
    price_staff = None
    vegetarian = None
    vegan = None
    allergens = None

    def __init__(self, day: date, title: str, price: Decimal,
                 price_staff: Decimal, vegetarian: bool, vegan: bool,
                 allergens: Set[str]):
        self.day = day
        self.title = title
        self.price = price
        self.price_staff = price_staff
        self.vegetarian = vegetarian
        self.vegan = vegan
        self.allergens = allergens

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<Serving {}>'.format(str(self))


class CanteenResult:
    opening_times = None
    servings = None

    def __init__(self, opening_times: Dict[int, Tuple[time, time]],
                 servings: List[Serving]):
        self.opening_times = opening_times
        self.servings = servings
