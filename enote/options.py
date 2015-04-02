#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Troels Kofoed Jacobsen

import os
import ConfigParser
import argparse
from tools import LogLevel

config_file = '$HOME/.config/enote.cfg'
defaults = {
    'basedir': '$HOME/enote',
    'output_format': 'txt',
    'sandbox': 'False',
    'max_notes': '1000',
    }
opts = {
    'basedir': 'str',
    'output_format': 'str',
    'token': 'str',
    'sandbox': 'bool',
    'max_notes': 'int',
    }

def parse_arguments():
    #TODO: move description to __init__.py (so both this file and setup.py can read)
    parser = argparse.ArgumentParser(description='Command line utility to backup Evernote notes and notebooks.')
    #TODO: wirite help lines
    
    ## Commands
    parser.add_argument('command')
    
    ## Options
    parser.add_argument('--profile', type=str)
    parser.add_argument('--basedir', type=str)
    parser.add_argument('-fmt', '--output_format', type=str)
    parser.add_argument('--token', type=str)
    parser.add_argument('--sandbox', type=bool)
    parser.add_argument('-N', '--max_notes', type=int)
    parser.add_argument('-v', '--verbose', action='store_true' )
    parser.add_argument('-q', '--quiet', action='store_true' )

    ## Filter options
    parser.add_argument('-n', '--notebook', type=str)
    parser.add_argument('-t', '--tags', type=str, nargs='+')

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
