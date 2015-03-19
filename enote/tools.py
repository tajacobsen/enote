#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Troels Kofoed Jacobsen

import html2text
import re
import string

def htmltotxt(content):
    text = html2text.html2text(content)
    text = text.strip("\n")
    return re.sub(r"\n{2,}","\n", text)

def clean_filename(text):
    allowed = ' _-.()æøåÆØÅ%s%s'%(string.letters, string.digits)
    return ''.join([c for c in text if c in allowed])
