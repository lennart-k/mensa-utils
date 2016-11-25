#!/usr/bin/env python3
"""Fetch and display canteen plans."""
import re
from datetime import date, datetime
from typing import Generator

import requests


def fetch_canteen(day_param: int, canteen_link: str) -> (date, Generator):
    """Generate output. day_param should be the number used by upstream."""
    return get_plan_data(canteen_link.format(date.today().year, day_param))


def get_plan_data(url) -> (date, Generator):
    """Fetch plan and get data."""
    plan = fetch_plan(url)

    return parse_plan_date(plan), parse_plan_foods(plan)


def parse_plan_date(plan: str) -> date:
    """Parse the plan date."""
    pattern = re.compile(r'\d{1,2}\.\d{1,2}\.\d{4}')
    # TODO: ensure that there has been a match
    plan_date_str = pattern.search(plan).group(0)
    plan_date = datetime.strptime(plan_date_str, '%d.%m.%Y').date()
    return plan_date


def parse_plan_foods(plan: str) -> Generator:
    """Parse a plan. Additionally return the date of the plan."""

    pattern = re.compile(
        r'class="dish-description">(.*?)</td>.*?(\d+,\d+).*?(\d+,\d+)',
        flags=re.DOTALL)

    foods = pattern.findall(plan)

    # remove unnecessary things from foods
    patterns = [
        (re.compile(r'\n|\r|<br />', flags=re.DOTALL), r''),
        (re.compile(r'<img [^>]*>', flags=re.DOTALL), r''),
        (re.compile(r'^ *', flags=re.DOTALL), r''),
        (re.compile(r'^ *$', flags=re.DOTALL), r''),
        (re.compile(r' *$', flags=re.DOTALL), r''),
        (re.compile(r' *,', flags=re.DOTALL), r','),
    ]

    for food in foods:
        vegetarian = False
        if re.search(r'Vegetarisch|Vegan', food[0], re.IGNORECASE):
            vegetarian = True
        replaced = food[0]
        replaced = remove_nested_brackets(replaced)
        for pattern in patterns:
            replaced = pattern[0].sub(pattern[1], replaced)
        price_regex = re.compile(r'(\d+),(\d+)')
        price_match = price_regex.search(food[1])
        price = '{:2d},{:02d}'.format(
            int(price_match.group(1)), int(price_match.group(2)))
        price_staff_match = price_regex.search(food[2])
        price_staff = '{:2d},{:02d}'.format(
            int(price_staff_match.group(1)), int(price_staff_match.group(2)))
        yield {
            'vegetarian': vegetarian,
            'price': price,
            'price_staff': price_staff,
            'title': replaced,
        }


def fetch_plan(url) -> str:
    """Fetch raw plan data."""
    return requests.get(url).text


def remove_nested_brackets(string):
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
