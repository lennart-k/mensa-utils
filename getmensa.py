#!/usr/bin/env python3
"""Fetch and display canteen plans."""
import re
import requests
from collections import defaultdict
from jinja2 import Template

CANTEENS = [
    ('Bucerius Law School',
        'http://speiseplan.studierendenwerk-hamburg.de/de/410/2016/{}/'),
    ('Café CFEL',
        'http://speiseplan.studierendenwerk-hamburg.de/de/680/2016/{}/'),
    ('Café Jungiusstraße',
        'http://speiseplan.studierendenwerk-hamburg.de/de/610/2016/{}/'),
    ('Campus',
        'http://speiseplan.studierendenwerk-hamburg.de/de/340/2016/{}/'),
    ('Geomatikum',
        'http://speiseplan.studierendenwerk-hamburg.de/de/540/2016/{}/'),
    ('Philturm',
        'http://speiseplan.studierendenwerk-hamburg.de/de/350/2016/{}/'),
    ('Stellingen',
        'http://speiseplan.studierendenwerk-hamburg.de/de/580/2016/{}/'),
    ('Studhaus',
        'http://speiseplan.studierendenwerk-hamburg.de/de/310/2016/{}/'),
]


def main():
    """Generate output."""
    days = [0, 99]
    mensa_data = defaultdict(list)
    for day in days:
        for canteen in CANTEENS:
            mensa_data[day].append((canteen[0], fetch_plan(canteen[1].format(day))))

    # pass output to jinja2
    with open("mensa.html") as template_file:
        template = Template(template_file.read())
        print(template.render({'mensa_data': mensa_data}))


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
    main()
