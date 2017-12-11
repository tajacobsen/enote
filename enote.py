#!/usr/bin/env python3

SANDBOX = False

import sys #DEBUG

import os, io
import argparse
import re
import string
import unicodedata

import enml

from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import NoteSortOrder

def clean_filename(text):
    text = unicodedata.normalize("NFKD", text)
    allowed = " _-.()æøåÆØÅ%s%s"%(string.ascii_letters, string.digits)
    return "".join([c for c in text if c in allowed])

def main():
    parser = argparse.ArgumentParser(prog="enote")            
    parser.add_argument("--path", type=str)
    parser.add_argument("--config", type=str)
    args = parser.parse_args()

    path = os.getcwd()
    if args.path is not None:
        path = args.path

    config_file = os.path.join(os.getcwd(), ".enote")
    if args.config is not None:
        config_file = args.config

    f = io.open(config_file, "r")
    token = f.readline().strip("\n")
    f.close()
    
    client = EvernoteClient(token=token, sandbox=SANDBOX)
    note_store = client.get_note_store()
    for notebook in note_store.listNotebooks():
        notebook_dir = os.path.join(path, clean_filename(notebook.name))
        print("Synchronizing notebook: {} -> {}".format(notebook.name, notebook_dir))
        if not os.path.isdir(notebook_dir):
            os.mkdir(notebook_dir)

        kwargs = {"order": NoteSortOrder.UPDATED} 
        kwargs["notebookGuid"] = notebook.guid
        note_filter = NoteFilter(**kwargs)
        
        #TODO: Figure out a way to know if more than 250 notes exist in notebook and handle accordingly
        offset = 0
        max_notes = 250
        max_notes = 2 #DEBUG

        result_spec = NotesMetadataResultSpec(
            includeTitle=True,
            includeUpdated=True
            )

        notes = note_store.findNotesMetadata(token, note_filter, offset, max_notes, result_spec).notes
        for note in notes:
            note_path = os.path.join(notebook_dir, clean_filename(note.title) + ".txt")
            do_download = True
            if os.path.isfile(note_path):
                if os.path.getmtime(note_path) == note.updated/1000:
                    do_download = False
             
            if do_download:
                content = note_store.getNoteContent(token, note.guid)
                #TODO: download and save ref. data
                content = enml.ENMLToText(content)
                content = content.strip("\n")
                content = re.sub(r"\n{2,}","\n", content)

                f = io.open(note_path, "w")
                f.write(content)
                f.write("\n")
                f.close()
                
                #os.utime(note_path, (-1, note.updated/1000))

        #TODO: Delete unneeded files
        sys.exit(0)

if __name__ == "__main__":
    main()
