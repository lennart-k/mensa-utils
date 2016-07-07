#!/usr/bin/env python3
"""Fetch and display canteen plans."""
import re
import requests

CANTEENS = [
    ('Philturm',
        'http://speiseplan.studierendenwerk-hamburg.de/de/350/2016/0/'),
    ('Studhaus',
        'http://speiseplan.studierendenwerk-hamburg.de/de/310/2016/0/'),
    ('Stellingen',
        'http://speiseplan.studierendenwerk-hamburg.de/de/580/2016/0/'),
]


def main():
    """Main routine."""
    for canteen in CANTEENS:
        print(canteen[0])
        fetch_plan(canteen[1])


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
        replaced = food[0]
        replaced = remove_nested_brackets(replaced)
        for pattern in patterns:
            replaced = pattern[0].sub(pattern[1], replaced)
        print('  {}'.format(replaced))


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
