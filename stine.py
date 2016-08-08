#!/usr/bin/env python3
"""Some stine pseudo-api tools."""
from argparse import ArgumentParser


if __name__ == '__main__':
    parser = ArgumentParser(description='Pseudo-API for stine.')
    subparsers = parser.add_subparsers()

    parser_startsession = subparsers.add_parser(
        'startsession', help='Authenticate for a new session.')

    parser_getexams = subparsers.add_parser(
        'getexams', help='Get current exam results.')
    parser_getexams.add_argument('foo', help='Foo Bar')

    arguments = parser.parse_args()
    print(arguments.action)
