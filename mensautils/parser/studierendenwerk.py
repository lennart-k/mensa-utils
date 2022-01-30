#!/usr/bin/env python3
"""Fetch and display canteen plans."""
import json
import re
import requests

from bs4 import BeautifulSoup
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple

from mensautils.parser.canteen_result import CanteenResult, Serving

WEEKDAYS = {
    'Montag': 1,
    'Dienstag': 2,
    'Mittwoch': 3,
    'Donnerstag': 4,
    'Freitag': 5,
    'Samstag': 6,
    'Sonntag': 7,
}


def get_canteen_data(canteen_number: int) -> CanteenResult:
    """Get information about canteen."""
    base_url = 'https://www.studierendenwerk-hamburg.de/speiseplan/'

    today_url = base_url
    today_plan = requests.get(today_url).text
    next_day_url = base_url + '?t=next_day'
    next_day_plan = requests.get(next_day_url).text

    servings = _parse_day_plan(today_plan, canteen_number) + _parse_day_plan(next_day_plan, canteen_number)

    opening_times = _parse_opening_times(today_plan, canteen_number)

    return CanteenResult(opening_times, servings)


def _parse_opening_times(plan: str, canteen_number: int) -> Dict[int, Tuple[time, time]]:
    """Parse opening times from a plan."""
    parsed_plan = BeautifulSoup(plan, 'html.parser')

    location = parsed_plan.find(attrs={'data-location': canteen_number})
    if not location:
        return {}
    opening_times_str = location.attrs['data-openings']
    opening_times = json.loads(opening_times_str)
    # These opening times are weird because they contain the opening times and the meal serving times
    # but no way to differentiate between them. We just take the last information. That might be the serving times.
    opening_times_parsed = {}

    for row in opening_times['openings']:
        start = row['dayFrom']
        end = row['dayTo']
        start_time = row['timeFrom'].removesuffix('Uhr').strip()
        end_time = row['timeTo'].removesuffix('Uhr').strip()
        if not start:
            continue

        first_day = WEEKDAYS[start]
        if end:
            last_day = WEEKDAYS[end]
        else:
            last_day = first_day

        if first_day > last_day:
            # invalid data.
            continue

        start_hour = datetime.strptime(start_time, '%H:%M').time()
        end_hour = datetime.strptime(end_time, '%H:%M').time()

        day = first_day
        while day <= last_day:
            opening_times_parsed[day] = start_hour, end_hour
            day += 1

    return opening_times_parsed


def _parse_day_plan(plan: str, canteen_number: int) -> List[Serving]:
    """Parse a day plan for its date and all servings."""
    parsed_plan = BeautifulSoup(plan, 'html.parser')

    canteen_section = parsed_plan.find(attrs={'data-location-id': canteen_number})
    if not canteen_section:
        return []
    menus = canteen_section.find_all(attrs={'class': 'menue-tile'})
    if not menus:
        return []

    # get date of plan
    date_string = canteen_section.find(attrs={'class': 'tx-epwerkmenu-menu-timestamp-active'}).attrs['data-timestamp']
    plan_date = datetime.strptime(date_string, '%Y-%m-%d').date()

    # get servings
    servings = []

    for menu in menus[1:]:
        if not menu:
            continue

        menu_name = menu.find(attrs={'class': 'singlemeal__headline'}).text.strip()

        price = Decimal(0)
        price_staff = Decimal(0)

        for info in menu.find_all(attrs={'class': 'singlemeal__info'}):
            if 'Studierende' in info.text:
                price = _parse_price(info.text)
            elif 'Bedienstete' in info.text:
                price_staff = _parse_price(info.text)

        allergens = set(menu.attrs['data-allergens'].split())

        # search for vegetarian & vegan
        symbols = [int(symbol) for symbol in menu.attrs['data-symbols'].split()]
        vegetarian = 31 in symbols
        vegan = 38 in symbols

        menu_name = _remove_nested_brackets(menu_name).strip()

        # remove spaces before followed by comma
        pattern = re.compile(r'\s+,')
        menu_name = pattern.sub(',', menu_name)

        serving = Serving(plan_date, menu_name, price, price_staff, vegetarian, vegan, allergens)

        servings.append(serving)

    return servings


def _parse_price(price: str) -> Decimal:
    """Parse a price from a string."""
    price_pattern = re.compile(r'(\d+),(\d+)')
    price = price_pattern.search(price)
    if price is not None:
        return Decimal('{}.{}'.format(price.group(1), price.group(2)))
    else:
        return Decimal(0)


def _current_monday(day: date):
    """Get the monday of current week."""
    while day.weekday() != 0:
        day -= timedelta(days=1)
    return day


def _remove_nested_brackets(string):
    """Remove nested brackets by iterating through the string."""
    new_string = ''
    appending = True
    brackets_count = 0
    for char in string:
        if char == '(':
            appending = False
            brackets_count += 1

        if appending:
            new_string += char

        if char == ')':
            brackets_count -= 1
            if brackets_count <= 0:
                appending = True
    return new_string
