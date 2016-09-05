#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2016 Troels Agergaard Jacobsen

SANDBOX = True

import sys
import os
import io
import pickle
import argparse

from __init__ import __description__
from auth import ENoteAuth

class ENote():
    def __init__(self, token):
        self.token = token
        self.client = EvernoteClient(token=token, sandbox=True)

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

    path = os.getcwd()
    config_file = os.path.join(path, '.enote')

    if command == 'init':
        enauth = ENoteAuth() 
        token = enauth.get_token()
        #TODO: This will wipe the file. If we store other variables in the future, need to find different way
        f = io.open(config_file, 'wb')
        pickle.dump(token, f)
        f.close()
        sys.exit(0)

    if not os.path.isfile(os.path.join(path, '.enote')):
        #TODO: write to stderr
        print 'Directory not initialized'
        sys.exit(1)

    f = io.open(config_file, 'rb')
    token = pickle.load(f)
    f.close()

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
