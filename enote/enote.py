#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2016 Troels Agergaard Jacobsen

import argparse
from __init__ import __description__

def main():
    parser = argparse.ArgumentParser(prog='enote', description=__description__)            
    subparser = parser.add_subparsers(dest='command')

    # init command
    parser_init = subparser.add_parser('init', help='Initialize directory and authenticate user')

    # list-notebooks command
    parser_list_notebooks = subparser.add_parser('list-notebooks', help='List available notebooks')

    # list-tags command
    parser_list_tags = subparser.add_parser('list-tags', help='List available tags')

    # list-notes command
    parser_list_notes = subparser.add_parser('list-notes', help='List notes')
    parser_list_notes.add_argument('--notebook', type=str, help='Limit search to specified notebook')
    parser_list_notes.add_argument('--tag', type=str, help='Limit search to specified tag')

    # download command
    parser_download = subparser.add_parser('download', help='Download notes')
    parser_download.add_argument('--notebook', type=str, help='Limit search to specified notebook')
    parser_download.add_argument('--tag', type=str, help='Limit search to specified tag')
    parser_download.add_argument('--delete', action='store_true', help='Delete extraneous files')
    parser_download.add_argument('--incremental', action='store_true', help='Only download new notes')

    args = parser.parse_args()
    command = args.command

    if command == 'init':
        raise NotImplementedError('init command not implemented')

    if command == 'list-notebooks':
        raise NotImplementedError('list-notebooks command not implemented')

    if command == 'list-tags':
        raise NotImplementedError('list-tags command not implemented')

    if command == 'list-notes':
        raise NotImplementedError('list-notes command not implemented')

    if command == 'download':
        raise NotImplementedError('download command not implemented')

if __name__ == "__main__":
    main()
