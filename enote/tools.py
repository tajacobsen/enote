#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2016 Troels Agergaard Jacobsen

import html2text
import re
import string

from enmltohtml import enmltohtml

def htmltotxt(content):
    text = html2text.html2text(content)
    text = text.strip("\n")
    return re.sub(r"\n{2,}","\n", text)

def enmltotxt(content):
    return htmltotxt(enmltohtml(content))

def clean_filename(text):
    allowed = ' _-.()æøåÆØÅ%s%s'%(string.letters, string.digits)
    return ''.join([c for c in text if c in allowed])
