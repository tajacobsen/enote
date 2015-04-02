#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Troels Kofoed Jacobsen
import os, io, sys
# Requred as evernote notes are unicode
reload(sys)
sys.setdefaultencoding('utf-8')

from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import NoteSortOrder

from enmltohtml import enmltohtml
from tools import htmltotxt, clean_filename, LogLevel, Logger

import options

class Note:
    def __init__(self, title, guid, notebook_name, tags, content, logger=Logger()):
        self.title = title
        self.guid = guid
        self.notebook_name = notebook_name
        self.tags = tags
        self.content = content
        self.logger = logger

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
            self.logger.log('Writing \"%s\" to %s'%(self.title, filename), LogLevel.VERBOSE)
            f = io.open(filename, 'w')
            self.pprint(f, fmt)
            f.close()
            self.logger.log(' - OK\n', LogLevel.VERBOSE)
        else:
            self.logger.log('Unable to write \"%s\" (no content)\n'%(self.title, ))

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
    def __init__(self, token, sandbox = False, max_notes = 1000, logger=Logger()):
        self.token = token
        self.logger = logger
        self.client = EvernoteClient(token=token, sandbox=sandbox)
        self.logger.log('Initializing Note Store')
        self.note_store = self.client.get_note_store()
        self.logger.log(' - OK\n')

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
        self.logger.log('Downloading Meta Data')
        result_list = self.note_store.findNotesMetadata(self.token, note_filter, offset, self.max_notes, result_spec)
        self.logger.log(' - OK\n')

        self.logger.log('Downloading %i Notes\n'%(len(result_list.notes),))
        for note in result_list.notes:
            if note.tagGuids is not None:
                tags = [self.tags[tag] for tag in note.tagGuids]
            else:
                tags = []

            self.logger.log('Downloading Note Content: \"%s\"'%(note.title), LogLevel.VERBOSE)
            note_content = None
            for i in range(3):
                if note_content is None:
                    try:
                        note_content = self.note_store.getNoteContent(self.token, note.guid)
                        self.logger.log(' - OK\n', LogLevel.VERBOSE)
                    except:
                        if i < 2:
                            self.logger.log(' - retrying...', LogLevel.VERBOSE)
                        else:
                            self.logger.log(' - FAILED\n', LogLevel.VERBOSE)

            self.notes.append(Note(
                note.title,
                note.guid,
                self.notebooks[note.notebookGuid],
                tags,
                note_content,
                logger=self.logger
                ))

    def writeNotes(self, basedir, fmt="txt"):
        self.logger.log('Writing %i Notes\n'%(len(self.notes),))
        for note in self.notes:
            note.write(basedir, fmt=fmt)


def main():
    config = options.get_config()
    logger = Logger(config['log_level'])
    enote = ENote(config['token'], config['sandbox'], config['max_notes'], logger=logger)
    enote.getNotes()
    enote.writeNotes(config['basedir'], fmt=config['output_format'])

if __name__ == "__main__":
    main()
