#!/usr/bin/env python2
# Copyright (c) 2015 Troels Kofoed Jacobsen

import html2text
import re

#TODO: Replace with some custom code
def htmltotxt(content):
    text = html2text.html2text(content)
    text = text.strip("\n")
    return re.sub(r"\n{2,}","\n", text)

