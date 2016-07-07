#!/usr/bin/env python3
"""Fetch and display canteen plans."""
import re
import requests
import sys

CANTEENS = [
    ('Philturm',
     'http://speiseplan.studierendenwerk-hamburg.de/de/350/2016/{}/'),
    ('Studhaus',
     'http://speiseplan.studierendenwerk-hamburg.de/de/310/2016/{}/'),
    ('Stellingen',
     'http://speiseplan.studierendenwerk-hamburg.de/de/580/2016/{}/'),
    ('Campus',
     'http://speiseplan.studierendenwerk-hamburg.de/de/340/2016/{}/'),
]


def main():
    """Main routine."""
    day = '0'
    if len(sys.argv) >= 2:
        if sys.argv[1] in ['0', '99']:
            day = sys.argv[1]
    if day == '0':
        print('Heute')
        print('=' * 30)
        print('')
    elif day == '99':
        print('Morgen')
        print('=' * 30)
        print('')
    for canteen in CANTEENS:
        print('V     €  {}'.format(canteen[0]))
        fetch_plan(canteen[1].format(day))
        print('\n')


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
        vegetarian = ' '
        if re.search(r'Vegetarisch|Vegan', food[0]):
            vegetarian = 'x'
        replaced = food[0]
        replaced = remove_nested_brackets(replaced)
        for pattern in patterns:
            replaced = pattern[0].sub(pattern[1], replaced)
        price_regex = re.compile(r'(\d+),(\d+)')
        price_match = price_regex.search(food[1])
        price = '{:2d},{:2d}'.format(
            int(price_match.group(1)), int(price_match.group(2)))
        print('{} {}  {}'.format(vegetarian, price, replaced))


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
