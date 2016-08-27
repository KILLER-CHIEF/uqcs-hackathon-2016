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
        self.app = App.instance
        return

    def open(self):
        print("WebSocket opened")
        self.player = Player()
        self.gameSession = None

    def on_message(self, message):
        self.write_message(u"You said: " + message)
        splitCommand = message.split(':')
        if not len(splitCommand) == 2:
            self.write_message(u"invalid:Invalid Packet!")
            return
        command, data = tuple(splitCommand)
        if command == "getboard":
            pass

    def on_close(self):
        print("WebSocket closed")

class LobbyPageHandler(RequestHandler):
    def get(self):
        self.render('lobby.html')

class NewGamePageHandler(RequestHandler):
    def get(self):
        self.render('new_game.html')

class GamePageHandler(RequestHandler):
    def get(self):
        self.write("game page")

class ReasourceHandler(RequestHandler):
    def get(self, filename):
        if filename.endswith('.js'):
            self.set_header("Content-Type", 'text/javascript')
        elif filename.endswith('.css'):
            response.set_header("Content-Type", 'text/css')
        else:
            # just leave the header
            pass

        # load file
        with open('reasource/' + filename, 'r') as file:
            self.write(file.read())


class App(Application):
    instance = None
    def __init__(self):
        App.instance = self
        settings = {}
        tornado.web.Application.__init__(self, [
            (r"/", LobbyPageHandler),
            (r"/index", LobbyPageHandler),
            (r"/new", NewGamePageHandler),
            (r"/game", GamePageHandler),
            (r'/websocket', PlayerHandler),
        ])

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
