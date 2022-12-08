#!/usr/bin/env python3
"""Fetch and display canteen plans."""
import re
import requests

from bs4 import BeautifulSoup
from datetime import datetime, time
from decimal import Decimal
from typing import Dict, List, Tuple

from mensautils.parser.canteen_result import CanteenResult, Serving


WEEKDAYS = {
    'montag': 1,
    'dienstag': 2,
    'mittwoch': 3,
    'donnerstag': 4,
    'freitag': 5,
    'samstag': 6,
    'sonntag': 7,
}

SHORT_WEEKDAY_NAMES = {
    'Mo': 'montag',
    'Di': 'dienstag',
    'Mi': 'mittwoch',
    'Do': 'donnerstag',
    'Fr': 'freitag',
    'Sa': 'samstag',
    'So': 'Sonntag',
}


def get_canteen_data(english: bool = False) -> CanteenResult:
    """Get information about canteen."""
    url = f'https://desy.myalsterfood.de/{"en" if english else "de"}/'

    response = requests.get(url)
    response.encoding = response.apparent_encoding
    week_plan = response.text

    servings = _parse_full_plan(week_plan, english=english)
    opening_times = _parse_opening_times(week_plan, english=english)

    return CanteenResult(opening_times, servings)


def _parse_opening_times(plan: str, english: bool = False) -> Dict[int, Tuple[time, time]]:
    """Parse opening times from a plan."""
    parsed_plan = BeautifulSoup(plan, 'html.parser')

    openings_div = parsed_plan.find('div', {'id': 'openings'})
    openings_strings = openings_div.find('p').strings
    for string in openings_strings:
        if string == ('Kantine' if not english else 'Canteen'):
            opening_string = next(openings_strings)
            break
    else:
        # No opening times for 'Kantine' found
        return {}

    return _extract_opening_times([opening_string])


def _parse_full_plan(plan: str, english: bool = False) -> List[Serving]:
    """Parse the plan for all dates and all servings."""
    parsed_plan = BeautifulSoup(plan, 'html.parser')

    servings = []
    days = parsed_plan.find_all('div', {'class': 'entry'})
    for day in days:
        try:
            date_string = day.attrs['id']
            plan_date = datetime.strptime(date_string, 'entry-%Y-%m-%d')

            items = day.find_all('table', {'class': 'entry'})
            parsed_items =  [_parse_item(plan_date, item, english=english) for item in items]
            servings += [item for item in parsed_items if item]
        except:
            continue

    return servings


FILTER_ITEMS = {'Tagessuppe mit Einlage', 'Preis per 100g', 'Soup of the day with extras'}


def _parse_item(plan_date, item, english: bool = False) -> Serving:
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
        lambda el: el.name == 'p' and ('Allergene' in el.text or 'allergens' in el.text))
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
    price_pattern = re.compile(r'€ (\d+)(?:[,\.])(\d+)')
    price = price_pattern.search(price)
    return Decimal('{}.{}'.format(price.group(1), price.group(2)))


def _extract_opening_times(rows):
    opening_times = {}

    weekdays_regex = '|'.join(SHORT_WEEKDAY_NAMES)

    single_day_pattern = re.compile(
        r'({})\.?\s*,? (\d+.\d+)\s*-\s*(\d+\.\d+)'.format(
            weekdays_regex), flags=re.IGNORECASE)

    multiple_day_pattern = re.compile(
        r'({})\.?\s*-\s*({})\.?\s*,? (\d+\.\d+)\s*-\s*(\d+\.\d+)'.format(
            *[weekdays_regex] * 2), flags=re.IGNORECASE)
    for row in rows:
        multiple = multiple_day_pattern.search(row)
        if multiple:
            first_day = WEEKDAYS[SHORT_WEEKDAY_NAMES[multiple.group(1)]]
            last_day = WEEKDAYS[SHORT_WEEKDAY_NAMES[multiple.group(2)]]
            if first_day > last_day:
                # invalid data.
                continue

            # Sometimes, a colon is used instead of a point
            start = multiple.group(3).replace(':', '.')
            end = multiple.group(4).replace(':', '.')

            start_hour = datetime.strptime(start, '%H.%M').time()
            end_hour = datetime.strptime(end, '%H.%M').time()

            day = first_day
            while day <= last_day:
                opening_times[day] = start_hour, end_hour
                day += 1

            continue
        single = single_day_pattern.search(row)
        if single:
            day = WEEKDAYS[SHORT_WEEKDAY_NAMES[single.group(1)]]

            # Sometimes, a colon is used instead of a point
            start = single.group(2).replace(':', '.')
            end = single.group(3).replace(':', '.')

            start_hour = datetime.strptime(start, '%H.%M').time()
            end_hour = datetime.strptime(end, '%H.%M').time()

            opening_times[day] = start_hour, end_hour

    return opening_times

