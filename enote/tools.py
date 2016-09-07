#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (c) 2016 Troels Agergaard Jacobsen

import html2text
import re
import string


from enmltohtml import enmltohtml

def htmltotxt(content):
    text = html2text.html2text(content)
    text = text.strip("\n")
    return re.sub(r"\n{2,}","\n", text)

def enmltotxt(content):
    return htmltotxt(enmltohtml(content))

def clean_filename(text):
    allowed = ' _-.()æøåÆØÅ%s%s'%(string.letters, string.digits)
    return ''.join([c for c in text if c in allowed])

#FIXME: The following is a required workaround as Evernote depends on bundled
#       thrift that is not compatible
import sys
from evernote.api.client import EvernoteClient, Store
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.notestore.NoteStore as NoteStore

import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient

class ENEvernoteClient(EvernoteClient):
    def get_user_store(self):
        user_store_uri = self._get_endpoint("/edam/user")
        store = ENStore(self.token, UserStore.Client, user_store_uri)
        return store

    def get_note_store(self):
        user_store = self.get_user_store()
        note_store_uri = user_store.getNoteStoreUrl()
        store = ENStore(self.token, NoteStore.Client, note_store_uri)
        return store

class ENStore(Store):
    def _get_thrift_client(self, client_class, url):
        http_client = THttpClient.THttpClient(url)
        #FIXME: Following line is broken
        #http_client.addHeaders(**{
        http_client.setCustomHeaders({
            'User-Agent': "%s / %s; Python / %s;"
            % (self._user_agent_id, self._get_sdk_version(), sys.version.replace('\n',""))
        })

        thrift_protocol = TBinaryProtocol.TBinaryProtocol(http_client)
        return client_class(thrift_protocol)
