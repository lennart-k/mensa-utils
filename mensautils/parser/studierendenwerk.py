#!/usr/bin/env python3
"""Fetch and display canteen plans."""
import re
import requests

from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple

from mensautils.parser.canteen_result import CanteenResult, Serving
from mensautils.parser.common import extract_opening_times


def get_canteen_data(canteen_number: int) -> CanteenResult:
    """Get information about canteen."""
    base_url = 'http://speiseplan.studierendenwerk-hamburg.de/de/{}/{}/{}/'

    today = date.today()

    today_url = base_url.format(canteen_number, today.year, 0)
    today_plan = requests.get(today_url).text
    next_day_url = base_url.format(canteen_number, today.year, 99)
    next_day_plan = requests.get(next_day_url).text

    servings = _parse_day_plan(today_plan) + _parse_day_plan(next_day_plan)

    opening_times = _parse_opening_times(today_plan)

    return CanteenResult(opening_times, servings)


def _parse_opening_times(plan: str) -> Dict[int, Tuple[time, time]]:
    """Parse opening times from a plan."""
    parsed_plan = BeautifulSoup(plan, 'html.parser')

    paragraph = parsed_plan.find('div', id='cafeteria')
    rows = paragraph.text.split('\n')
    return extract_opening_times(rows)


def _parse_day_plan(plan: str) -> List[Serving]:
    """Parse a day plan for its date and all servings."""
    parsed_plan = BeautifulSoup(plan, 'html.parser')

    main_table = parsed_plan.find('table')
    if not main_table:
        return []
    rows = main_table.find_all('tr')
    if not rows:
        return []

    # get date of plan
    date_string = rows[0].find('th').text
    pattern = re.compile(r'\d+\.\d+\.\d+')
    date_match = pattern.search(date_string).group(0)
    plan_date = datetime.strptime(date_match, '%d.%m.%Y').date()

    # get servings
    servings = []

    for row in rows[1:]:
        row = row.find_all('td')
        if not row:
            continue

        # get prices
        price = _parse_price(row[1].text)
        price_staff = _parse_price(row[2].text)

        servings.append(_parse_dish_title(plan_date, price, price_staff,
                        row[0]))

    return servings


def _parse_price(price: str) -> Decimal:
    """Parse a price from a string."""
    price_pattern = re.compile(r'(\d+),(\d+)')
    price = price_pattern.search(price)
    return Decimal('{}.{}'.format(price.group(1), price.group(2)))


def _parse_dish_title(day: date, price: Decimal, price_staff: Decimal,
                      title: Tag) -> Serving:
    """Parse a dish title for its informationto populate a serving."""
    title_str = str(title)
    title_text = title.text.strip()

    # search for allergens
    allergen_pattern = re.compile(r'title="?([^>"]*)"?>')
    allergens = set(allergen_pattern.findall(title_str))

    # search for vegetarian
    vegetarian = 'vegetarisch' in title_str

    # search for vegan
    vegan = 'Vegan' in title_str

    title_text = _remove_nested_brackets(title_text).strip()

    # remove spaces before followed by comma
    pattern = re.compile(r'\s+,')
    title_text = pattern.sub(',', title_text)

    return Serving(
        day, title_text, price, price_staff, vegetarian, vegan, allergens)


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
