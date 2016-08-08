#!/usr/bin/env python3
"""Some stine pseudo-api tools."""
from argparse import ArgumentParser
from getpass import getpass
import pickle
import re
import requests


STINE_BASE_URL = 'https://www.stine.uni-hamburg.de/'
STINE_ENCODING = 'UTF-16LE'


def start_session(arguments):
    """Start a new session."""
    username = input('Username: ')
    password = getpass()
    session = requests.Session()

    # get stine home page (for required cookies)
    home_page = session.get(STINE_BASE_URL)
    home_page.encoding = STINE_ENCODING

    # search for main link for german language
    pattern = re.compile(r'href="([^"]*)">de<')
    match = pattern.search(home_page.text)
    if not match:
        print('Invalid stine home page.')
        return
    a = session.get(STINE_BASE_URL + match.group(1))
    # return

    # try to authenticate
    login_result = session.post(
        STINE_BASE_URL + 'scripts/mgrqispi.dll', data={
            'usrname': username,
            'pass': password,
            'APPNAME': 'CampusNet',
            'PRGNAME': 'LOGINCHECK',
            'ARGUMENTS': 'clino,usrname,pass,menuno,menu_type,browser,platform',
            'clino': '000000000000001',
            'menuno': '000000',
            'menu_type': 'classic',
            'browser': '',
            'platform': '',
        })
    error_pattern = re.compile(r'Kennung oder Kennwort falsch')
    if error_pattern.search(login_result.text):
        print('Access denied.')
        return

    with open(arguments.session_file, 'wb') as session_file:
        pickle.dump(session, session_file)
    print('Session successfully initiated.')


if __name__ == '__main__':
    parser = ArgumentParser(description='Pseudo-API for stine.')
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    parser_startsession = subparsers.add_parser(
        'startsession', help='Authenticate for a new session.')
    parser_startsession.add_argument(
        '-s', '--session-file', nargs='?', default='./stine_session',
        dest='session_file', help='The file to store the session data in.')

    parser_getexams = subparsers.add_parser(
        'getexams', help='Get current exam results.')

    arguments = parser.parse_args()
    if arguments.subcommand == 'startsession':
        start_session(arguments)
