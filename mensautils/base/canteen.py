#!/usr/bin/env python3
"""Fetch and display canteen plans."""
import re
from datetime import date

import requests


def fetch_canteen(day: date, canteen_link: str) -> dict:
    """Generate output."""
    today = date.today()
    day_param = 99
    if day == today:
        day_param = 0
    return fetch_plan(canteen_link.format(day.year, day_param))


def fetch_plan(url):
    """Fetch and parse a plan."""
    plan = requests.get(url)

    pattern = re.compile(
        r'class="dish-description">(.*?)</td>.*?(\d+,\d+).*?(\d+,\d+)',
        flags=re.DOTALL)

    foods = pattern.findall(plan.text)

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
