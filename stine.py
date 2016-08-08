#!/usr/bin/env python3
"""Some stine pseudo-api tools."""
from argparse import ArgumentParser


def start_session(arguments):
    """Start a new session."""
    pass


if __name__ == '__main__':
    parser = ArgumentParser(description='Pseudo-API for stine.')
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    parser_startsession = subparsers.add_parser(
        'startsession', help='Authenticate for a new session.')
    parser_startsession.add_argument(
        '-s', '--session-file', nargs='?', default='./stine_session',
        help='The file to store the session data in.')

    parser_getexams = subparsers.add_parser(
        'getexams', help='Get current exam results.')

    arguments = parser.parse_args()
    print(arguments)
