#!/usr/bin/env python3
"""Fetch and display canteen plans."""
import re
from datetime import datetime, timedelta

import requests
from django.conf import settings


def fetch_mensa() -> dict:
    """Generate output."""
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    year = today.year
    days = [(0, today), (99, tomorrow)]  # TODO: this will probably break on friday (at least a bit)

    mensa_data = {}
    for day in days:
        mensa_data[day[0]] = day[1], []
        for canteen in settings.CANTEENS:
            # generate list of generator to iterate multiple times
            mensa_data[day[0]][1].append(
                (canteen[0],
                 list(fetch_plan(canteen[1].format(year, day[0])))))

    return mensa_data


def fetch_plan(url):
    """Fetch and parse a plan."""
    plan = requests.get(url)

    pattern = re.compile(
        r'class="dish-description">(.*?)</td>.*?(\d+,\d+)',
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
        yield {
            'vegetarian': vegetarian,
            'price': price,
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

if __name__ == '__main__':
    print(fetch_mensa())
