#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Troels Kofoed Jacobsen
import os, io, sys, time
# Requred as evernote notes are unicode
reload(sys)
sys.setdefaultencoding('utf-8')

from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import NoteSortOrder

import tools
from tools import LogLevel, Logger

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
    
        tools.mkdir(outdir)
        
        if self.content is not None:
            filename = '%s/%s.%s'%(outdir, tools.clean_filename(self.title), fmt)
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
            f.write(unicode(tools.enmltohtml(self.content)))
            f.write(u"\n")
        elif fmt == "txt":
            f.write(u"TITLE: %s\n" % (self.title,))
            for tag in self.tags:
                f.write(u"TAG: %s\n" % (tag,))
            f.write(unicode(tools.enmltotxt(self.content)))
            f.write(u"\n")

class ENote:
    def __init__(self, token, basedir, sandbox=False, max_notes=1000, logger=Logger()):
        self.token = token
        self.basedir = basedir
        self.logger = logger
        self.client = EvernoteClient(token=token, sandbox=sandbox)
        self.logger.log('Initializing Note Store')
        self.note_store = self.client.get_note_store()
        self.logger.log(' - OK\n')
        self.curtime = time.time()

        self.notebooks = {}
        for notebook in self.note_store.listNotebooks():
            self.notebooks[notebook.guid] = notebook.name

        self.notes = []

        self.tags = {}
        for tag in self.note_store.listTags():
            self.tags[tag.guid] = tag.name

        self.max_notes = max_notes

    def getNotesMetaData(self, notebook=None, tags=None, days=None, diff=False):
        kwargs = {'order': NoteSortOrder.UPDATED} 
        if notebook is not None:
            try:
                notebookGuid = [item[0] for item in self.notebooks.items() if item[1] == notebook][0]
                kwargs['notebookGuid'] = notebookGuid
            except:
                self.logger.log('ERROR: Could not find notebook: %s\n'%(notebook,), LogLevel.QUIET)
                sys.exit(1)
        if tags is not None:
            tagGuids = [item[0] for item in self.tags.items() if item[1] in tags]
            kwargs['tagGuids'] = tagGuids

        note_filter = NoteFilter(**kwargs)

        offset = 0
        result_spec = NotesMetadataResultSpec(
            includeTitle=True,
            includeNotebookGuid=True,
            includeTagGuids=True,
            includeUpdated=True
            )
        self.logger.log('Downloading Meta Data')
        result_list = self.note_store.findNotesMetadata(self.token, note_filter, offset, self.max_notes, result_spec)
        self.logger.log(' - OK\n')

        if diff:
            lastrun = tools.read_lastrun(self.basedir)
            return [note for note in result_list.notes if (note.updated/1000L) >= long(lastrun)]
        elif days is not None:
            return [note for note in result_list.notes if (note.updated/1000L) >= (long(self.curtime) - (60*60*24*days))]
        else:
            return result_list.notes

    def getNotes(self, notebook=None, tags=None, days=None, diff=False):
        result_list = self.getNotesMetaData(notebook, tags, days, diff)

        self.logger.log('Downloading %i Notes\n'%(len(result_list),))
        for note in result_list:
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

    def writeNotes(self, fmt="txt"):
        self.logger.log('Writing %i Notes\n'%(len(self.notes),))
        for note in self.notes:
            note.write(self.basedir, fmt=fmt)

        tools.write_lastrun(self.basedir, self.curtime)

    def listNotes(self, notebook=None, tags=None, days=None, diff=False):
        result_list = self.getNotesMetaData(notebook, tags, days, diff)
        notes = []

        for note in result_list:
            notes.append('%s/%s'%(self.notebooks[note.notebookGuid],note.title))

        notes.sort()

        for note in notes:
            self.logger.log('%s\n'%(note,))

    def listNotebooks(self):
        notebooks = self.notebooks.values()
        notebooks.sort()
        for notebook in notebooks:
            self.logger.log('%s\n'%(notebook,))

    def listTags(self):
        tags = self.tags.values()
        tags.sort()
        for tag in tags:
            self.logger.log('%s\n'%(tag,))

def main():
    config, command, notebook, tags = options.get_config()
    logger = Logger(config['log_level'])
    enote = ENote(
        config['token'], 
        config['basedir'],
        config['sandbox'],
        config['max_notes'],
        logger=logger
        )
    if command == 'pull':
        enote.getNotes(notebook, tags, config['days'], config['diff'])
        enote.writeNotes(fmt=config['output_format'])
    elif command == 'list':
        enote.listNotes(notebook, tags, config['days'], config['diff'])
    elif command == 'list-notebooks':
        enote.listNotebooks()
    elif command == 'list-tags':
        enote.listTags()

if __name__ == "__main__":
    main()
