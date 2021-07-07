#!/usr/bin/env python3
"""Fetch and display canteen plans."""
import re
import requests

from bs4 import BeautifulSoup
from datetime import datetime, time
from decimal import Decimal
from typing import Dict, List, Tuple

from mensautils.parser.canteen_result import CanteenResult, Serving


def get_canteen_data() -> CanteenResult:
    """Get information about canteen."""
    url = 'https://desy.myalsterfood.de/de/'

    response = requests.get(url)
    response.encoding = response.apparent_encoding
    week_plan = response.text

    servings = _parse_full_plan(week_plan)
    opening_times = _parse_opening_times(week_plan)

    return CanteenResult(opening_times, servings)


def _parse_opening_times(plan: str) -> Dict[int, Tuple[time, time]]:
    """Parse opening times from a plan."""
    parsed_plan = BeautifulSoup(plan, 'html.parser')
    opening_times = {}

    # FIXME

    return opening_times


def _parse_full_plan(plan: str) -> List[Serving]:
    """Parse the plan for all dates and all servings."""
    parsed_plan = BeautifulSoup(plan, 'html.parser')

    servings = []
    days = parsed_plan.find_all('div', {'class': 'entry'})
    for day in days:
        try:
            date_string = day.attrs['id']
            plan_date = datetime.strptime(date_string, 'entry-%Y-%m-%d')

            items = day.find_all('table', {'class': 'entry'})
            parsed_items =  [_parse_item(plan_date, item) for item in items]
            servings += [item for item in parsed_items if item]
        except:
            continue

    return servings


FILTER_ITEMS = {'Tagessuppe', 'Preis per 100g'}


def _parse_item(plan_date, item) -> Serving:
    imgs = item.find_all('img', attrs={'class': 'category-icons'})
    srcs = [im.attrs['src'] for im in imgs if 'src' in im.attrs]
    is_vegetarian = any('icon-vegetarian' in src for src in srcs)
    is_vegan = any('icon-vegan' in src for src in srcs)

    price = _parse_price(item.text)

    # titles[0] should be German, titles[1] English
    titles = [s for s
                in (st.strip() for st in item.find('td').strings)
                if s]
    if titles[0] in FILTER_ITEMS:
        return None

    allergen_p = item.find(
        lambda el: el.name == 'p' and 'Allergene' in el.text)
    if allergen_p:
        allergen_string = allergen_p.text
        allergen_pattern = re.compile(r'(\d+\.?\d?)\)')
        allergens = set(allergen_pattern.findall(allergen_string))
    else:
        allergens = set()

    return Serving(plan_date, ' / '.join(titles), price, price,
                   is_vegetarian, is_vegan, allergens)


def _parse_price(price: str) -> Decimal:
    """Parse a price from a string."""
    price_pattern = re.compile(r'€ (\d+),(\d+)')
    price = price_pattern.search(price)
    return Decimal('{}.{}'.format(price.group(1), price.group(2)))
