#!/usr/bin/env python3
"""Some stine pseudo-api tools."""
from argparse import ArgumentParser
from getpass import getpass
import pickle
import re
import requests


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

    with open(arguments.session_file, 'wb') as session_file:
        pickle.dump({
            'session': session,
            'home_url': login_result.url,
        }, session_file)
    print('Session successfully initiated.')


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

    arguments = parser.parse_args()
    if arguments.subcommand == 'startsession':
        start_session(arguments)
