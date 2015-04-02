#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Troels Kofoed Jacobsen

import os
import ConfigParser
import argparse

config_file = '$HOME/.config/enote.cfg'
defaults = {
        'basedir': '$HOME/enote',
        'output_format': 'txt',
        'sandbox': 'False',
        'max_notes': '1000',
        }

def read_config():
    userconfig = ConfigParser.ConfigParser(defaults)
    userconfig.read(os.path.expandvars(config_file))

    config = {}
    config['basedir'] = os.path.expandvars(userconfig.get("enote", "basedir"))
    config['output_format'] = userconfig.get("enote", "output_format")
    config['token'] = userconfig.get("enote", "token")
    config['sandbox'] = userconfig.getboolean("enote", "sandbox")
    config['max_notes'] = userconfig.getint("enote", "max_notes")

    return config

def parse_arguments():
    #TODO: move description to __init__.py (so both this file and setup.py can read)
    parser = argparse.ArgumentParser(description='Command line utility to backup Evernote notes and notebooks.')
    #TODO: wirite help lines
    parser.add_argument('--basedir', type=str)
    parser.add_argument('-fmt', '--output_format', type=str)
    parser.add_argument('--token', type=str)
    parser.add_argument('--sandbox', type=bool)
    parser.add_argument('-N', '--max_notes', type=int)
    args = parser.parse_args()
    return args


def get_config():
    config = read_config()
    args = parse_arguments()
    if args.basedir is not None:
        config['basedir'] = args.basedir
    if args.output_format is not None:
        config['output_format'] = args.output_format
    if args.token is not None:
        config['token'] = args.token
    if args.sandbox is not None:
        config['sandbox'] = args.sandbox
    if args.basedir is not None:
        config['max_notes'] = args.max_notes

    return config
