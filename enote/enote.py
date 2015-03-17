#!/usr/bin/env python2
# Copyright (c) 2015 Troels Kofoed Jacobsen
import os, io, sys
# Requred as evernote notes are unicode
reload(sys)
sys.setdefaultencoding("utf-8")

import ConfigParser
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec

from enmltohtml import enmltohtml
from tools import htmltotxt

config_file = "$HOME/.config/enote.cfg"

class Note:
    def __init__(self, title, guid, notebook_name, tags, content):
        self.title = title
        self.guid = guid
        self.notebook_name = notebook_name
        self.tags = tags
        self.content = content

    def write(self, basedir):
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

        f = io.open(outdir + "/" + self.title + ".txt", "w")
        self.pprint(f)
        f.close()

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
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.client = EvernoteClient(token = auth_token, sandbox = True)
        self.note_store = self.client.get_note_store()

        self.notebooks = {}
        for notebook in self.note_store.listNotebooks():
            self.notebooks[notebook.guid] = notebook.name

        self.notes = []

        self.tags = {}
        for tag in self.note_store.listTags():
            self.tags[tag.guid] = tag.name

    def getNotes(self, notebook=None, tag=None):
        #TODO: fix to include notebook
        #notebookGuid = 
        #TODO: fix to include tag(s)
        note_filter = NoteFilter()

        offset = 0
        max_notes = 10
        result_spec = NotesMetadataResultSpec(includeTitle=True, includeNotebookGuid=True, includeTagGuids=True)
        result_list = self.note_store.findNotesMetadata(self.auth_token, note_filter, offset, max_notes, result_spec)
        for note in result_list.notes:
            if note.tagGuids is not None:
                tags = [self.tags[tag] for tag in note.tagGuids]
            else:
                tags = []
            self.notes.append(Note(
                note.title,
                note.guid,
                self.notebooks[note.notebookGuid],
                tags,
                self.note_store.getNoteContent(self.auth_token, note.guid)
                ))

def main():
    config = ConfigParser.ConfigParser()
    config.read(os.path.expandvars(config_file))
    basedir = os.path.expandvars(config.get("enote", "basedir"))
    access_token = config.get("enote", "token")

    enote = ENote(access_token)
    enote.getNotes()
    for note in enote.notes:
        note.pprint(fmt="txt")

if __name__ == "__main__":
    main()
