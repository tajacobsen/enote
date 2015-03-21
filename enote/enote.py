#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Troels Kofoed Jacobsen
import os, io, sys
# Requred as evernote notes are unicode
reload(sys)
sys.setdefaultencoding('utf-8')

import ConfigParser
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import NoteSortOrder

from enmltohtml import enmltohtml
from tools import htmltotxt, clean_filename

import config

class Note:
    def __init__(self, title, guid, notebook_name, tags, content):
        self.title = title
        self.guid = guid
        self.notebook_name = notebook_name
        self.tags = tags
        self.content = content

    def write(self, basedir, fmt="txt"):
        if basedir[-1] == "/":
            outdir = basedir + self.notebook_name
        else:
            outdir = basedir + "/" + self.notebook_name
    
        # Not possible to mkdir to create all dirs in one go. Therefore need to
        # iterate through directory tree and create all non-existing dirs
        dirtree = outdir.split("/")
        for i in range(2, len(dirtree) + 1):
            subpath = "/".join(dirtree[:i])
            if not os.path.isdir(subpath):
                os.mkdir(subpath)
        
        if self.content is not None:
            filename = '%s/%s.%s'%(outdir, clean_filename(self.title), fmt)
            sys.stdout.write('Writing \"%s\" to %s'%(self.title, filename))
            sys.stdout.flush()
            f = io.open(filename, 'w')
            self.pprint(f, fmt)
            f.close()
            sys.stdout.write(' - OK\n')
            sys.stdout.flush()
        else:
            sys.stdout.write('Unable to write \"%s\" (no content)\n'%(self.title, ))
            sys.stdout.flush()

    def pprint(self, f=sys.stdout, fmt="txt"):
        if fmt == "enml":
            f.write(u"<!--TITLE: %s-->\n" % (self.title,))
            for tag in self.tags:
                f.write(u"<!--TAG: %s-->\n" % (tag,))
            f.write(unicode(self.content))
            f.write(u"\n")
        elif fmt == "html":
            f.write(u"<!--TITLE: %s-->\n" % (self.title,))
            for tag in self.tags:
                f.write(u"<!--TAG: %s-->\n" % (tag,))
            f.write(unicode(enmltohtml(self.content)))
            f.write(u"\n")
        elif fmt == "txt":
            f.write(u"TITLE: %s\n" % (self.title,))
            for tag in self.tags:
                f.write(u"TAG: %s\n" % (tag,))
            f.write(unicode(htmltotxt(enmltohtml(self.content))))
            f.write(u"\n")

class ENote:
    def __init__(self, auth_token, sandbox = False, max_notes = 1000):
        self.auth_token = auth_token
        self.client = EvernoteClient(token = auth_token, sandbox = sandbox)
        sys.stdout.write('Initializing Note Store')
        sys.stdout.flush()
        self.note_store = self.client.get_note_store()
        sys.stdout.write(' - OK\n')
        sys.stdout.flush()

        self.notebooks = {}
        for notebook in self.note_store.listNotebooks():
            self.notebooks[notebook.guid] = notebook.name

        self.notes = []

        self.tags = {}
        for tag in self.note_store.listTags():
            self.tags[tag.guid] = tag.name

        self.max_notes = max_notes

    def getNotes(self, notebook=None, tag=None):
        #TODO: fix to include notebook
        #notebookGuid = 
        #TODO: fix to include tag(s)
        note_filter = NoteFilter(order=NoteSortOrder.UPDATED)
        #TODO: add filter by newest (updated)

        offset = 0
        result_spec = NotesMetadataResultSpec(includeTitle=True, includeNotebookGuid=True, includeTagGuids=True)
        sys.stdout.write('Downloading Meta Data')
        sys.stdout.flush()
        result_list = self.note_store.findNotesMetadata(self.auth_token, note_filter, offset, self.max_notes, result_spec)
        sys.stdout.write(' - OK\n')
        sys.stdout.flush()
        for note in result_list.notes:
            if note.tagGuids is not None:
                tags = [self.tags[tag] for tag in note.tagGuids]
            else:
                tags = []

            sys.stdout.write('Downloading Note Content: \"%s\"'%(note.title))
            sys.stdout.flush()
            note_content = None
            for i in range(3):
                if note_content is None:
                    try:
                        note_content = self.note_store.getNoteContent(self.auth_token, note.guid)
                        sys.stdout.write(' - OK\n')
                    except:
                        if i < 2:
                            sys.stdout.write(' - retrying...')
                        else:
                            sys.stdout.write(' - FAILED\n')
                    sys.stdout.flush()

            self.notes.append(Note(
                note.title,
                note.guid,
                self.notebooks[note.notebookGuid],
                tags,
                note_content
                ))

    def writeNotes(self, basedir, fmt="txt"):
        for note in self.notes:
                note.write(basedir, fmt=fmt)

def main():
    userconfig = ConfigParser.ConfigParser(config.defaults)
    userconfig.read(os.path.expandvars(config.config_file))
    basedir = os.path.expandvars(userconfig.get("enote", "basedir"))
    output_format = userconfig.get("enote", "output_format")
    access_token = userconfig.get("enote", "token")
    sandbox = userconfig.getboolean("enote", "sandbox")
    max_notes = userconfig.getint("enote", "max_notes")

    enote = ENote(access_token, sandbox, max_notes)
    enote.getNotes()
    enote.writeNotes(basedir, fmt=output_format)

if __name__ == "__main__":
    main()
