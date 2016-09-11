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
from MultogoGameSession import GameState

define("port", default=8888, help="run on the given port", type=int)

class PlayerHandler(WebSocketHandler):

	def open(self):
		self.app = App.instance
		print("WebSocket opened")
		self.gameId = None

	def on_message(self, message):
		#self.write_message(u"You said: " + message)
		splitCommand = message.split(':')
		if not len(splitCommand) == 2:
			self.write_message(u"invalid:Invalid Packet!")
			return
		command, data = tuple(splitCommand)
		#---------- Public Requests ----------
		if command == "ping":
			self.write_message(u"ping:Pong!")
			return
		elif command == "postdata":
			if data.isdigit() and int(data):
				gameHandler = App.instance.gameHandlers.get(int(data), None)
				if gameHandler is not None:
					gameHandler.sendPostGameReport(self)
				else:
					self.write_message(u"info:Game %d does not exist!" % int(data))
				return
		elif command == "join":
			gameId = 0
			if data.isdigit() and int(data):
				gameId = int(data)
			gameHandler = App.instance.gameHandlers.get(gameId, None)
			if gameHandler == None:
				self.write_message(u"invalid:That game does not exist!")
				return
			gameHandler.addPlayer(self)
			self.gameId = gameId
			return
		elif command == "status":
			if data.isdigit() and int(data):
				gameHandler = App.instance.gameHandlers.get(int(data), None)
				if gameHandler is not None:
					self.write_message(u"status:%d" % gameHandler.gameState)
				else:
					self.write_message(u"info:Game %d does not exist!" % int(data))
				return
			
		gameHandler = App.instance.gameHandlers.get(self.gameId, None)
		#--- Valid Game Handle ---
		if gameHandler == None:
			self.write_message(u"invalid:You are not in a Game!")
		#---------- Game Requests ----------
		elif command == "board":
			board = ""
			for i in gameHandler.board.board:
				if i == None:
					board += '.'
				else:
					board += gameHandler.players[int(i)].getSymbol()
			self.write_message(u"board:"+str(gameHandler.board.getWidth())+','+str(gameHandler.board.getHeight())+','+board)
		elif command == "status":
			self.write_message(u"status:%d" % gameHandler.gameState)
		elif command == "postdata":
			gameHandler.sendPostGameReport(self)
		#---------- Pre-Game ----------
		elif command == "startgame":
			if gameHandler.gameState == GameState.PreGame:
				playerId = gameHandler.getPlayerIdFromInstance(self)
				if playerId == 0:
					gameHandler.startGame()
				else:
					self.write_message(u"info:You do not have permission to start the game!")
			else:
				self.write_message(u"info:The game has already started!")
		#---------- In-Game ---------
		elif command == "move":
			if not gameHandler.gameState == GameState.InGame:
				self.write_message(u"info:The game is not in progress!")
				return
			playerId = gameHandler.getPlayerIdFromInstance(self)
			if playerId == None:
				self.write_message(u"invalidmove:")
				self.write_message(u"alert:You are not in a game!")
				return
			if not gameHandler.playerTurnIndex == playerId:
				self.write_message(u"noturturn:")
				return
			else:
				if gameHandler.makeMove(data):
					return
			self.write_message(u"invalidmove:")
			return
		else:
			self.write_message(u"unknown:%s" % message)

	def on_close(self):
		print("WebSocket closed")
		gameHandler = App.instance.gameHandlers.get(self.gameId, None)
		if gameHandler is not None:
			playerId = gameHandler.getPlayerIdFromInstance(self)
			if playerId is not None:
				gameHandler.removePlayer(playerId)
				print("Player %d removed from game %d." % (playerId,self.gameId))
			else:
				print("Player does not seem to be in game %d!" % self.gameId)
		

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
			self.write("<script>alert('That game does not exist!');</script>");
			self.write("<script>location.href='/';</script>");
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
			self.set_header("Content-Type", 'text/css')
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
            (r'/reasource/(.+.js)',ReasourceHandler),
            (r'/reasource/(.+.css)',ReasourceHandler),
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
