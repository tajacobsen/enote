#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2016 Troels Agergaard Jacobsen
# Requred as evernote notes are unicode
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

SANDBOX = False

import os
import io
import pickle
import argparse

#FIXME: Workaround (see tools.py for description)
#from evernote.api.client import EvernoteClient
from tools import ENEvernoteClient as EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import NoteSortOrder

from __init__ import __description__
from auth import ENoteAuth
from tools import enmltotxt, clean_filename

class ENote():
    def __init__(self, token, path):
        self.token = token
        self.path = path
        self.client = EvernoteClient(token=token, sandbox=SANDBOX)
        self.note_store = self.client.get_note_store()

        self.notebooks = None
        self.tags = None

        self.notes = []

    def pullNotebooks(self):
        if self.notebooks is None:
            self.notebooks = {}
            for notebook in self.note_store.listNotebooks():
                self.notebooks[notebook.guid] = notebook.name

    def listNotebooks(self):
        self.pullNotebooks()
        notebooks = self.notebooks.values()
        notebooks.sort()
        return notebooks

    def printNotebooks(self):
        for notebook in self.listNotebooks():
            sys.stdout.write(notebook)
            sys.stdout.write('\n')

    def pullTags(self):
        if self.tags is None:
            self.tags = {}
            for tag in self.note_store.listTags():
                self.tags[tag.guid] = tag.name

    def listTags(self):
        self.pullTags()
        tags = self.tags.values()
        tags.sort()
        return tags

    def printTags(self):
        for tag in self.listTags():
            sys.stdout.write(tag)
            sys.stdout.write('\n')

    def pullNotesGuid(self, notebookGuid, tagGuids=None):
        kwargs = {'order': NoteSortOrder.UPDATED} 
        kwargs['notebookGuid'] = notebookGuid
        kwargs['tagGuids'] = tagGuids
        note_filter = NoteFilter(**kwargs)
        
        #TODO: Figure out a way to know if more than 250 notes exist in notebook and handle accordingly
        offset = 0
        max_notes = 250

        result_spec = NotesMetadataResultSpec(
            includeTitle=True,
            includeNotebookGuid=True,
            includeTagGuids=True,
            includeUpdated=True
            )

        result_list = self.note_store.findNotesMetadata(self.token, note_filter, offset, max_notes, result_spec)
        self.notes += result_list.notes

    def pullNotes(self, notebook=None, tags=None):
        self.pullNotebooks()
        self.pullTags()

        if tags is not None:
            tagGuids = [item[0] for item in self.tags.items() if item[1] in tags]
        else:
            tagGuids = None
        
        if notebook is None:
            for notebookGuid in self.notebooks.keys():
                self.pullNotesGuid(notebookGuid, tagGuids)
        else:
            notebookGuid = [item[0] for item in self.notebooks.items() if item[1] == notebook][0]
            self.pullNotesGuid(notebookGuid, tagGuids)

    def listNotes(self, notebook=None, tags=None):
        self.pullNotes(notebook, tags)

        notes = []
        for note in self.notes:
            notes.append('%s/%s'%(self.notebooks[note.notebookGuid], note.title))

        notes.sort()
        return notes  

    def printNotes(self, notebook=None, tags=None):
        for note in self.listNotes(notebook, tags):
            sys.stdout.write(note)
            sys.stdout.write('\n')

    def writeNotes(self, notebook=None, tags=None, delete=False, incremental=False):
        self.pullNotes(notebook, tags)
        files = {}
        for note in self.notes:
            notebook_name = self.notebooks[note.notebookGuid]
            #TODO: Strip special characters
            notebook_dir = os.path.join(self.path, clean_filename(notebook_name))
            if not os.path.isdir(notebook_dir):
                os.mkdir(notebook_dir)

            note_path = os.path.join(notebook_dir, clean_filename(note.title) + '.txt')
            do_download = True
            if incremental and os.path.isfile(note_path):
                #To be on the safe side we always download notes when mtime does not match exactly
                if long(os.path.getmtime(note_path)) == note.updated/1000L:
                    do_download = False
                elif long(os.path.getmtime(note_path)) > note.updated/1000L:
                    sys.stderr.write('Warning: \"%s\" is newer than corresponding note, skipping.'%(note_path,))
                    sys.stderr.write('\n')
                    do_download = False

            if note_path in files.keys():
                sys.stderr.write('Warning: \"%s\" already written, skipping.'%(note_path,))
                sys.stderr.write('\n')
                do_download = False

            # Keep track of which files we download 
            files[note_path] = do_download

            if do_download:
                content = self.note_store.getNoteContent(self.token, note.guid)
                content = enmltotxt(content)

                f = io.open(note_path, 'w')
                f.write(unicode(content))
                f.write(u'\n')
                f.close()

                os.utime(note_path, (-1, note.updated/1000L))

        if delete:
            if notebook is None:
                notebook_names = [clean_filename(n) for n in self.notebooks.values()]
            else:
                notebook_names = [clean_filename(notebook)]

            dirs = [d for d in os.listdir(self.path) if os.path.isdir(d)]
            for d in dirs:
                # Only touch files in directories corresponding to notebooks in current search
                if d in notebook_names:
                    files_in_dir = [os.path.join(self.path, d, f) \
                            for f in os.listdir(os.path.join(self.path, d)) \
                            if os.path.isfile(os.path.join(self.path, d, f))]
                    for f in files_in_dir:
                        if not f in files:
                            sys.stderr.write('Warning: Deleting \"%s\"\n'%(f,))
                            os.remove(f)

def main():
    parser = argparse.ArgumentParser(prog='enote', description=__description__)            
    subparser = parser.add_subparsers(dest='command')

    # init command
    parser_init = subparser.add_parser('init', help='Initialize directory and authenticate user')

    # list-notebooks command
    parser_list_notebooks = subparser.add_parser('list-notebooks', help='List available notebooks')

    # list-tags command
    parser_list_tags = subparser.add_parser('list-tags', help='List available tags')

    # list-notes command
    parser_list_notes = subparser.add_parser('list-notes', help='List notes')
    parser_list_notes.add_argument('--notebook', type=str, help='Limit search to specified notebook')
    parser_list_notes.add_argument('--tags', type=str, help='Limit search to specified tags (comma separated list)')

    # download command
    parser_download = subparser.add_parser('download', help='Download notes')
    parser_download.add_argument('--notebook', type=str, help='Limit search to specified notebook')
    parser_download.add_argument('--tags', type=str, help='Limit search to specified tags (comma separated list)')
    parser_download.add_argument('--delete', action='store_true', help='Delete extraneous files')
    parser_download.add_argument('--incremental', action='store_true', help='Only download new notes')

    args = parser.parse_args()
    command = args.command

    path = os.getcwd()
    config_file = os.path.join(path, '.enote')

    if command == 'init':
        enauth = ENoteAuth() 
        token = enauth.get_token()
        #TODO: This will wipe the file. If we store other variables in the future, need to find different way
        f = io.open(config_file, 'wb')
        pickle.dump(token, f)
        f.close()
        sys.exit(0)

    if not os.path.isfile(os.path.join(path, '.enote')):
        #TODO: write to stderr
        sys.stderr.write('Error: Directory not initialized')
        sys.stderr.write('\n')
        sys.exit(1)

    f = io.open(config_file, 'rb')
    token = pickle.load(f)
    f.close()

    enote = ENote(token, path)

    if command == 'list-notebooks':
        enote.printNotebooks()

    if command == 'list-tags':
        enote.printTags()

    if command == 'list-notes':
        if args.tags is not None:
            tags = args.tags.split(',')
        else:
            tags = None

        enote.printNotes(args.notebook, tags)

    if command == 'download':
        if args.tags is not None:
            tags = args.tags.split(',')
        else:
            tags = None

        enote.writeNotes(args.notebook, tags, args.delete, args.incremental)

if __name__ == "__main__":
    main()
