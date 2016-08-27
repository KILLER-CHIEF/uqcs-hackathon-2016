#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging, os

import tornado.art
from tornado.httpserver import HTTPServer
import tornado.options

from tornado.escape import json_decode, json_encode
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.options import define, options
from tornado.template import Template, Loader
from tornado.web import RequestHandler, Application, authenticated
from tornado.websocket import WebSocketHandler

define("port", default=8888, help="run on the given port", type=int)

class PlayerWebSocket(WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")

class LobbyPageHandler(RequestHandler):
    def get(self):
        self.render('index.html')

class App(Application):
    def __init__(self):
        settings = {}
        tornado.web.Application.__init__(self, [
            tornado.web.url(r"/", LobbyPageHandler, name="lobby"),
            tornado.web.url(r'/websocket', PlayerWebSocket, name="ws"),
        ], **settings)

        #self.lobbyHandler = LobbyHandler(self)
        self.gameSessions = {}
        self.playerHandlers = {}

def main():
    tornado.art.show()
    options.parse_command_line()
    App().listen(options.port)
    IOLoop.instance().start()

if __name__ == "__main__":
    main()
