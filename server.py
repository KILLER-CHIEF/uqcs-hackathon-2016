#!/usr/bin/env python

import logging, os
import re

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
import GetLocalIP

define("port", default=27080, help="run on the given port", type=int)

class PlayerHandler(WebSocketHandler):

	def check_origin(self, origin):
		return super(PlayerHandler, self).check_origin(origin) \
			or bool(re.match(r"^.*?\.glitchyscripts\.com", origin))
	
	# Handle the player connection.
	#def __init__(self, *wargs, **kwargs):
	#	# A player has just been created!
	#	super(WebSocketHandler, self).__init__(*wargs, **kwargs)
	def init(self):
		#
		self.publicCommands = {
			"ping" : PlayerHandler.ping,
			"postdata" : PlayerHandler.postdata,
			"join" : PlayerHandler.join_game,
			"status" : PlayerHandler.status,
		}
		
		#
		self.gameCommands = {
			"board" : PlayerHandler.board,
			"players": PlayerHandler.players,
			"gamestatus": PlayerHandler.gamestatus,
			"gamepostdata": PlayerHandler.gamepostdata,
			"startgame" : PlayerHandler.startgame,
			"move" : PlayerHandler.move,
			"chat" : PlayerHandler.chat,
		}
	
	def open(self):
		self.app = App.instance
		print("WebSocket opened")
		self.gameId = None
		self.init()
	
	def on_message(self, message):
		firstColonIndex = message.find(':')
		if firstColonIndex <= 0:
			self.write_message(u"invalid:Invalid Packet!")
			return
		command = message[:firstColonIndex]
		data = message[firstColonIndex+1:]
		
		# Run the function assocciated with the command
		if command in self.publicCommands.keys():
			self.publicCommands[command](self, data)
		elif command in self.gameCommands.keys():
			gameHandler = App.instance.gameHandlers.get(self.gameId, None)
			#--- Valid Game Handle ---
			if gameHandler == None:
				self.write_message(u"invalid:You are not in a Game!")
				return
			self.gameCommands[command](self, data, gameHandler)
		else:
			self.write_message(u"unknown:%s" % message)
	
	
	#---------- Public Requests ----------
	def ping(self, data):
		self.write_message(u"ping:Pong!")
	
	def postdata(self, data):
		if data.isdigit() and int(data):
			gameHandler = App.instance.gameHandlers.get(int(data), None)
			if gameHandler is not None:
				gameHandler.sendPostGameReport(self)
			else:
				self.write_message(u"info:Game %d does not exist!" % int(data))
	
	def join_game(self, data):
		gameId = 0
		if data.isdigit() and int(data):
			gameId = int(data)
		gameHandler = App.instance.gameHandlers.get(gameId, None)
		if gameHandler == None:
			self.write_message(u"invalid:That game does not exist!")
			return
		gameHandler.addPlayer(self)
		self.gameId = gameId
	
	def status(self, data):
		if data.isdigit() and int(data):
			gameHandler = App.instance.gameHandlers.get(int(data), None)
			if gameHandler is not None:
				self.write_message(u"status:%d" % gameHandler.gameState)
			else:
				self.write_message(u"info:Game %d does not exist!" % int(data))
	
	
	#---------- Game Requests ----------
	def board(self, data, gameHandler):
		board = ""
		for i in gameHandler.board.board:
			if i == None:
				board += '.'
			else:
				board += gameHandler.players[int(i)].getSymbol()
		self.write_message(u"board:"+str(gameHandler.board.getWidth())+','+str(gameHandler.board.getHeight())+','+board)
	
	def players(self, data, gameHandler):
		self.write_message(u"players:%s" % gameHandler.allPlayerDataToString())
	
	def gamestatus(self, data, gameHandler):
		self.write_message(u"status:%d" % gameHandler.gameState)
	
	def gamepostdata(self, data, gameHandler):
		gameHandler.sendPostGameReport(self)
	
	def chat(self, data, gameHandler):
		playerId = gameHandler.getPlayerIdFromInstance(self)
		if playerId == None:
			return
		text = data.replace("\n", " ").strip()
		if text == "":
			return
		text = "%c: %s" % (gameHandler.players[playerId].getSymbol(), text)
		print(text)
		for player in gameHandler.players:
			if player.client is not None:
				player.client.write_message(u"chat:%s" % text)
	
	#---------- Pre-Game ----------
	def startgame(self, data, gameHandler):
		if gameHandler.gameState == GameState.PreGame:
			playerId = gameHandler.getPlayerIdFromInstance(self)
			if playerId == 0:
				if len(gameHandler.players) > 1:
					gameHandler.startGame()
				else:
					self.write_message(u"info:Must have at least 2 players in game to start!")
			else:
				self.write_message(u"info:You do not have permission to start the game!")
		else:
			self.write_message(u"info:The game has already started!")
	
	
	#---------- In-Game ---------
	def move(self, data, gameHandler):
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
	
	def on_close(self):
		print("WebSocket closed")
		gameHandler = App.instance.gameHandlers.get(self.gameId, None)
		if gameHandler is not None:
			playerId = gameHandler.getPlayerIdFromInstance(self)
			if playerId is not None:
				gameHandler.removePlayer(playerId)
				if gameHandler.getPlayerCount() == 1: 
					print("Player %d left game %d." % (playerId,self.gameId))
					#print gameHandler.playersRemaining()[1]
					print("1 player left in game %d: Player  wins by default" % (self.gameId))
				elif gameHandler.getPlayerCount() == 0:
					print("All players have left game %d" % self.gameId)
				else:
					print("Player %d left game %d." % (playerId,self.gameId))
					
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
		if not max_players == "" and max_players.isdigit() and int(max_players) >= 2 and int(max_players) <= 26:
			max_players = int(max_players)
		else:
			max_players = ""
		
		if name == "" or width == "" or height == "" or max_players == "":
			error_response = "Incorrect Data!"
			if name == "":
				error_response = "The name of the lobby is incorrect!"
			elif max_players == "":
				error_response = "Incorrect number of players! Enter a value between 2 and 26."
			elif width == "" or height == "":
				error_response = "Incorrect board dimensions! Enter a value between 4 and a reasonable number."
			self.write_page(name, width, height, max_players, error_response)
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
		page = loader.load('game.html').generate(app=App.instance, joinGameId=gameId, websocketHostAddr="%s:%d" % (GetLocalIP.getLocalIP(), options.port))
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
	''' App is the webserver instance object. It is responsible for holding all
	the game instances and responding to HTTP requests.'''
	instance = None
	
	def __init__(self):
		'''Creates the server.'''
		
		App.instance = self # The can only be one
		self.usedGameId = 0
		
		# additional server settings
		settings = {'debug':True}
		
		# game instances
		self.gameHandlers = {}
		
		# HTTP resource handlers
		tornado.web.Application.__init__(self, [
			(r"/", LobbyPageHandler),
			(r"/index", LobbyPageHandler),
			(r"/new", NewGamePageHandler),
			(r"/game", GamePageHandler),
			(r'/websocket', PlayerHandler),
			(r'/reasource/(.+.js)',ReasourceHandler),
			(r'/reasource/(.+.css)',ReasourceHandler),
		], **settings)
	
	def getUniqueGameId(self):
		''' Gives you a unique game ID'''
		self.usedGameId += 1
		return self.usedGameId
	
	def createNewGameHandler(self, name, width, height, max_players):
		''''''
		gameId = self.getUniqueGameId()
		gameHandler = GameHandler(gameId, name.replace("[?]", str(gameId)), width, height, max_players)
		self.gameHandlers[gameId] = gameHandler
		return gameId
	

def main():
	''' Runs the server '''
	tornado.art.show()
	options.parse_command_line()
	#BindIP = GetLocalIP.getLocalIP()
	#BindIP = "127.0.0.1"
	App().listen(options.port)#, BindIP)
	IOLoop.instance().start()

if __name__ == "__main__":
	main()
