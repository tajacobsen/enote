#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Troels Kofoed Jacobsen
#from distutils.core import setup
from distutils.core import setup

from enote import __version__

setup(
    name='enote',
    version=__version__,
    license='MIT',
    description='Command line utility to backup Evernote notes and notebooks',
    author='Troels Jacobsen',
    author_email='tkjacobsen@gmail.com',
    url='https://github.com/tkjacobsen/enote',
    packages=['enote'],
    scripts=['bin/enote'],
    )
