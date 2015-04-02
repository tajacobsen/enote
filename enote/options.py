#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Troels Kofoed Jacobsen

import os
import ConfigParser

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
