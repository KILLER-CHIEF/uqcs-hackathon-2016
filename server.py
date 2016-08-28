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

from MultogoGameSession import GameHandler

define("port", default=8888, help="run on the given port", type=int)

class PlayerHandler(WebSocketHandler):

	def open(self):
		self.app = App.instance
		print("WebSocket opened")
		#self.player = Player()
		self.gameSession = None

	def on_message(self, message):
		self.write_message(u"You said: " + message)
		splitCommand = message.split(':')
		if not len(splitCommand) == 2:
			self.write_message(u"invalid:Invalid Packet!")
			return
		command, data = tuple(splitCommand)
		if command == "join":
			gameId = 0
			if data.isdigit() and int(data):
				gameId = int(data)
			gameHandler = App.instance.gameHandlers.get(gameId, None)
			if gameHandler == None:
				self.write_message(u"invalid:That game does not exist!")
				return
			GameHandler.addPlayer(self)
		elif command == "getboard":
			pass

	def on_close(self):
		print("WebSocket closed")

class NewGamePageHandler(RequestHandler):

	def write_page(response, new_name, new_width, new_height, new_max_players, new_error):
		loader = Loader('templates/')
		page = loader.load('newgame.html').generate(app=App.instance, name=new_name, width=new_width, height=new_height, max_players=new_max_players, error=new_error)
		response.write(page)
	
	def get(response):
		response.write_page("", "", "", "", "")
		
	def post(self):
		name = self.get_argument('name', "")
		width = self.get_argument('width', "")
		height = self.get_argument('height', "")
		max_players = self.get_argument('max_players', "")
		
		if name == "" or len(name) < 1:
			name = ""
		if not width == "" and width.isdigit() and int(width) >= 4:
			width = int(width)
		else:
			width = ""
		if not height == "" and height.isdigit() and int(height) >= 4:
			height = int(height)
		else:
			height = ""
		if not max_players == "" and max_players.isdigit() and int(max_players) >= 2:
			max_players = int(max_players)
		else:
			max_players = ""
		
		if name == "" or width == "" or height == "" or max_players == "":
			self.write_page(name, width, height, max_players, "Incorrect Data!")
			return
		
		gameId = App.instance.createNewGameHandler(name, width, height, max_players)
		print "New Game Created"
		self.redirect("/game?gameid="+str(gameId))
		
class LobbyPageHandler(RequestHandler):
	def get(response):
		loader = Loader('templates/')
		page = loader.load('lobby.html').generate(app=App.instance)
		response.write(page)

class GamePageHandler(RequestHandler):
	def get(self):
		gameId = self.get_argument('gameid', "")
		if not gameId == "" and gameId.isdigit() and int(gameId) > 0:
			gameId = int(gameId)
		else:
			gameId = 0
		gameHandler = App.instance.gameHandlers.get(gameId, None)
		if gameHandler == None:
			self.write("That game does not exist!")
			return
		#if not gameHandler.gameSession.gameState == 0:
		#	self.write("That game has already started!")
		#	return
		
		loader = Loader('templates/')
		page = loader.load('game.html').generate(app=App.instance, joinGameId=gameId)
		self.write(page)

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
		self.usedGameId = 0
		settings = {'debug':True}
		tornado.web.Application.__init__(self, [
			(r"/", LobbyPageHandler),
			(r"/index", LobbyPageHandler),
			(r"/new", NewGamePageHandler),
			(r"/game", GamePageHandler),
			(r'/websocket', PlayerHandler),
		], **settings)

		self.gameHandlers = {}
	
	def getUniqueGameId(self):
		self.usedGameId += 1
		return self.usedGameId
	
	def createNewGameHandler(self, name, width, height, max_players):
		gameId = self.getUniqueGameId()
		gameHandler = GameHandler(gameId, name, width, height, max_players)
		self.gameHandlers[gameId] = gameHandler
		return gameId
	

def main():
	tornado.art.show()
	options.parse_command_line()
	App().listen(options.port)
	IOLoop.instance().start()

if __name__ == "__main__":
	main()
