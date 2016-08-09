#!/usr/bin/env python3
"""Some stine pseudo-api tools."""
from argparse import ArgumentParser
from getpass import getpass
from time import sleep
import html
import os
import pickle
import re
import requests
import sys


STINE_BASE_URL = 'https://www.stine.uni-hamburg.de'


def start_session(arguments):
    """Start a new session."""
    username = input('Username: ')
    password = getpass()
    session = requests.Session()

    # get stine home page (for required cookies)
    home_page = session.get(STINE_BASE_URL)
    home_page.encoding = 'UTF-16LE'
    # search for main link for german language
    pattern = re.compile(r'href="([^"]*)">de<')
    match = pattern.search(home_page.text)
    if not match:
        print('Invalid stine home page.')
        return
    home_page = session.get(STINE_BASE_URL + match.group(1))
    home_page.encoding = 'utf-8'

    # follow redirection to actual start page
    home_page = _follow_stine_redirection_link(session, home_page)

    # get form from home page
    pattern = re.compile(r'<form name="cn_loginForm".*?</form>', re.DOTALL)
    form = pattern.search(home_page.text)
    field_pattern = re.compile(r'input name="([^"]*)".*?value="([^"]*)"')
    fields = field_pattern.findall(form.group(0))

    login_data = {
        'usrname': username,
        'pass': password
    }
    # add provided stine-fields
    for field_name, field_value in fields:
        login_data[field_name] = field_value

    # try to authenticate
    login_result = session.post(
        STINE_BASE_URL + '/scripts/mgrqispi.dll', data=login_data
    )
    error_pattern = re.compile(
        r'fehlgeschlagener Einloggversuche|Kennung oder Kennwort falsch')
    if error_pattern.search(login_result.text):
        print('Access denied.')
        return
    refresh_url = login_result.headers['REFRESH'][7:]
    home_page = session.get(STINE_BASE_URL + refresh_url)
    home_page = _follow_stine_redirection_link(session, home_page)

    _store_session(arguments.session_file, {
        'session': session,
        'home_url': home_page.url,
    })
    print('Session successfully initiated.')


def get_exams(arguments):
    """Get an overview of the exams."""
    watch_interval = int(arguments.watch)

    parsed_exams = _get_exams(arguments)
    print(parsed_exams)

    if watch_interval <= 0:
        return

    # watch
    while True:
        newly_parsed_exams = _get_exams(arguments)
        if parsed_exams != newly_parsed_exams:
            print('')
            print('a change has occured!')
            print('')
            print(newly_parsed_exams)
            print('')
            if arguments.notification:
                print('calling {}'.format(arguments.notification))
                os.system(arguments.notification)
        else:
            print('no change.')
        parsed_exams = newly_parsed_exams
        sleep(watch_interval * 60)


def _get_exams(arguments):
    """Load and parse the exam page."""
    session_data = _load_session(arguments.session_file)
    home_url = session_data['home_url']
    session = session_data['session']

    if 'exams_url' not in session_data:
        session_data['exams_url'] = _get_exams_page_link(session, home_url)
        _store_session(arguments.session_file, session_data)
    exams_page_link = session_data['exams_url']

    # get results page
    exams_page = session.get(exams_page_link)
    exams_page.encoding = 'utf-8'

    # get exams
    pattern = re.compile(r'<tr class="tbdata">.*?</tr>', re.DOTALL)
    exams = pattern.findall(exams_page.text)
    exam_pattern = re.compile(
        r'<td>\s*.*?&nbsp;.*?&nbsp;(.*?)<br />.*?\s*</td>.*?(\d,\d)',
        re.DOTALL)
    parsed_exams = ''
    for exam in exams:
        exam = exam_pattern.findall(exam)
        parsed_exams += '{} - {}\n'.format(exam[0][1], exam[0][0])

    # remove last newline
    parsed_exams = parsed_exams[:-1]

    return parsed_exams


def _follow_stine_redirection_link(session, response):
    """Follow the redirection link from stine."""
    pattern = re.compile(r'href="([^"]*)"[^>]*>Startseite<')
    match = pattern.search(response.text)
    if not match:
        print('Invalid stine home page.')
        return
    response = session.get(STINE_BASE_URL + match.group(1))
    response.encoding = 'utf-8'
    return response


def _get_exams_page_link(session, home_url):
    """Get the link of the exams result page."""
    # load home page to find "Studium" link
    home_page = session.get(home_url)
    pattern = re.compile(r'href="([^"]*)"[^>]*>Studium<')
    match = pattern.search(home_page.text)
    if not match:
        print('Invalid stine home page. Maybe your session is expired.')
        return

    # get "Studium" page and find results link
    study_page = session.get(STINE_BASE_URL + html.unescape(match.group(1)))
    pattern = re.compile(r'href="([^"]*)"[^>]*>Pr&uuml;fungsergebnisse<')
    match = pattern.search(study_page.text)
    if not match:
        print('Invalid stine home page. Maybe your session is expired.')
        return
    link = html.unescape(match.group(1))
    return STINE_BASE_URL + link


def _store_session(session_file, session_data):
    """Load the session from a pickled session file."""
    with open(session_file, 'wb') as session_file:
        pickle.dump(session_data, session_file)


def _load_session(session_file):
    """Load the session from a pickled session file."""
    if not os.path.isfile(session_file):
        print('invalid session file path.')
        sys.exit(1)
    try:
        with open(session_file, 'rb') as session_file:
            return pickle.load(session_file)
    except (TypeError, pickle.UnpicklingError):
        print('invalid session file path.')
        sys.exit(1)


if __name__ == '__main__':
    parser = ArgumentParser(description='Pseudo-API for stine.')
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    parser.add_argument(
        '-s', '--session-file', nargs='?', default='./stine_session',
        dest='session_file', help='The file to store the session data in.')

    parser_startsession = subparsers.add_parser(
        'startsession', help='Authenticate for a new session.')

    parser_getexams = subparsers.add_parser(
        'getexams', help='Get current exam results.')
    parser_getexams.add_argument(
        '-w', '--watch', default='-1', type=int,
        dest='watch', help='When greater than zero, the script runs '
        'as daemon and checks for new exams every N minutes.')
    parser_getexams.add_argument(
        '-n', '--notify',
        dest='notification', help='The specified command will be executed '
        'when there has been a change.')

    arguments = parser.parse_args()
    if arguments.subcommand == 'startsession':
        start_session(arguments)
    elif arguments.subcommand == 'getexams':
        get_exams(arguments)
