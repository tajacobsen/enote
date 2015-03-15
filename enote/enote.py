#!/usr/bin/env python2
import os, io
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec

class Note:
    def __init__(self, title, guid, notebook_name, notebook_guid, content):
        self.title = title
        self.guid = guid
        self.notebook_name = notebook_name
        self.notebook_guid = notebook_guid
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
        f.write(unicode(self.content))
        f.write(u"\n")
        f.close()
        #print self.notebook_name + "/" + self.title

class ENote:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.client = EvernoteClient(token=dev_token)
        self.note_store = self.client.get_note_store()

        self.notebooks = {}
        for notebook in self.note_store.listNotebooks():
            self.notebooks[notebook.guid] = notebook.name

        self.notes = []

    def getNotes(self, notebook=None, tag=None):
        #TODO: fix to include notebook
        #notebookGuid = 
        #TODO: fix to include tag(s)
        note_filter = NoteFilter()

        offset = 0
        max_notes = 10
        result_spec = NotesMetadataResultSpec(includeTitle=True, includeUpdated=True, includeNotebookGuid=True)
        result_list = self.note_store.findNotesMetadata(self.auth_token, note_filter, offset, max_notes, result_spec)
        for note in result_list.notes:
            self.notes.append(Note(
                note.title,
                note.guid,
                self.notebooks[note.notebookGuid],
                note.notebookGuid,
                self.note_store.getNoteContent(self.auth_token, note.guid)
                ))

        
#user_store = client.get_user_store()
#user = user_store.getUser()
#print user.username

#note_store = client.get_note_store()

#for notebook in notebooks:
#    print notebook.name
#    print notebook.guid

#tags = note_store.listTags()
#for tag in tags:
#    print tag.name

# notebookGuid = xxx



if __name__ == "__main__":
    basedir = "/home/tkjacobsen/enote"
    dev_token = "S=s1:U=9085b:E=15374ebb74a:C=14c1d3a8a30:P=1cd:A=en-devtoken:V=2:H=7e6bc64bcc94d790eff5760cb6257bd7"
    enote = ENote(dev_token)
    enote.getNotes()
    for note in enote.notes:
        note.write(basedir)

