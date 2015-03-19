Introduction
============
This program is a command line utility that can backup Evernote notes and notebooks.

The program is licensed under the MIT license.

Installation
============
## Dependencies:
* evernote-sdk-python-git (currently the bundled thrift library is required)
* python2-oauth2
* python2-beautifulsoup4
* python2-html2text-git (https://github.com/aaronsw/html2text)

## Configuration:
Create a configuration file named $HOME/.config/enote.cfg with the following content:

    [enote]
    token = XXX
