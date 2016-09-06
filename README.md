Introduction
============
This program is a command line utility that can backup Evernote notes and notebooks.

The program is licensed under the MIT license.

Installation
============
## Dependencies (FreeBSD pkg names):
* py27-evernote
* py27-html2text

Usage
=====
```shell
usage: enote [-h] {init,list-notebooks,list-tags,list-notes,download} ...

Command line utility to backup Evernote notes and notebooks.

positional arguments:
  {init,list-notebooks,list-tags,list-notes,download}
    init                Initialize directory and authenticate user
    list-notebooks      List available notebooks
    list-tags           List available tags
    list-notes          List notes
    download            Download notes

optional arguments:
  -h, --help            show this help message and exit
```

## list-notes command
```shell
usage: enote list-notes [-h] [--notebook NOTEBOOK] [--tags TAGS]

optional arguments:
  -h, --help           show this help message and exit
  --notebook NOTEBOOK  Limit search to specified notebook
  --tags TAGS          Limit search to specified tags (comma separated list)
```

## download command
```shell
usage: enote download [-h] [--notebook NOTEBOOK] [--tags TAGS] [--delete]
                      [--incremental]

optional arguments:
  -h, --help           show this help message and exit
  --notebook NOTEBOOK  Limit search to specified notebook
  --tags TAGS          Limit search to specified tags (comma separated list)
  --delete             Delete extraneous files
  --incremental        Only download new notes
```

Contributing
============
Pull requests and issues are welcome. I would specifically like support on implementing a proper OAuth flow. 
