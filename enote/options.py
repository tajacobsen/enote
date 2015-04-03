#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Troels Kofoed Jacobsen

import os
import ConfigParser
import argparse
from tools import LogLevel
from __init__ import __description__

config_file = '$HOME/.config/enote.cfg'
defaults = {
    'basedir': '$HOME/enote',
    'output_format': 'txt',
    'sandbox': False,
    'max_notes': 1000,
    'days': None,
    }
opts = {
    'basedir': 'str',
    'output_format': 'str',
    'token': 'str',
    'sandbox': 'bool',
    'max_notes': 'int',
    'days': 'long',
    }

def parse_arguments():
    parser = argparse.ArgumentParser(description=__description__)
    
    ## Commands
    parser.add_argument('command', help='One of: pull (download notes), list (list notes), list-notebooks, list-tags')
    
    ## Options
    parser.add_argument('--profile', type=str, help='Profile to load from enote.cfg')
    parser.add_argument('--basedir', type=str, help='Directory where notes are written')
    parser.add_argument('-fmt', '--output_format', type=str, help='Output format (enml|html|txt)')
    parser.add_argument('--token', type=str, help='Developer token (preferred to set in enote.cfg)')
    parser.add_argument('--sandbox', action='store_true', help='Point to sandbox.evernote.com')
    parser.add_argument('-N', '--max_notes', type=int, help='Max number of notes to fetch')
    parser.add_argument('-v', '--verbose', action='store_true' , help='Enable verbosity')
    parser.add_argument('-q', '--quiet', action='store_true', help='Shut up' )
    parser.add_argument('-d', '--days', type=long, help='Download only notes updated within DAYS days')

    ## Filter options
    parser.add_argument('-n', '--notebook', type=str, help='Download only notes in NOTEBOOK')
    parser.add_argument('-t', '--tags', type=str, nargs='+', help='Download only notes with TAGS')

    args = parser.parse_args()
    return args

def get(userconfig, section, key, opt_type):
    if opt_type == 'str':
        return userconfig.get(section, key)
    elif opt_type == 'int':
        return userconfig.getint(section, key)
    elif opt_type  == 'bool':
        return userconfig.getboolean(section, key)

def get_option(args, userconfig, profile, key, opt_type='str'):
    # arg > profile in cfg file > default in cfg file > default
    if vars(args).has_key(key) and vars(args)[key] is not None:
        return vars(args)[key]
    elif userconfig.has_option(profile, key):
        return get(userconfig, profile, key, opt_type)
    elif userconfig.has_option('enote', key):
        return get(userconfig, 'enote', key, opt_type)
    else:
        return defaults[key]

def get_config():
    args = parse_arguments()
    userconfig = ConfigParser.ConfigParser()
    userconfig.read(os.path.expandvars(config_file))

    if args.profile is not None:
        profile = args.profile
    elif userconfig.has_option('enote', 'profile'):
        profile = userconfig.get('enote', 'profile')
    else:
        profile = None

    config = {}
    if args.quiet:
        config['log_level'] = LogLevel.QUIET
    elif args.verbose:
        config['log_level'] = LogLevel.VERBOSE
    else:
        config['log_level'] = LogLevel.DEFAULT

    for opt in opts.keys():
        config[opt] = get_option(args, userconfig, profile, opt, opts[opt])
 
    config['basedir'] = os.path.expandvars(config['basedir'])

    notebook = args.notebook
    tags = args.tags

    return config, args.command, notebook, tags
