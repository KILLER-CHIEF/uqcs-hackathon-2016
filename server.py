#!/usr/bin/env python

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

class PlayerHandler(WebSocketHandler):
    def __init__(self, *argv, **argkw):
        super().__init__(self, *args, **kwargs)
        
        return

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
            tornado.web.url(r'/websocket', PlayerHandler, name="ws"),
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
