from datetime import datetime
import re


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


def extract_opening_times(rows):
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
