#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2016 Troels Agergaard Jacobsen

class ENoteAuth():
    def __init__(self):
        pass

    def get_token(self):
        token = raw_input('Request token from https://www.evernote.com/api/DeveloperToken.action and past it here: ')
        return token
