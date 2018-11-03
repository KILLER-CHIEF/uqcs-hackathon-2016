from MultogoBoard import Board
from MultogoPlayer import Player
from random import randint

class GameState(object):
	PreGame = 0
	InGame = 1
	PostGame = 2

class GameHandler(object):
	#
	
	def __init__(self, gameId, name, width, height, max_players):
		self.gameId = gameId
		self.name = name
		self.width = width
		self.height = height
		self.playersMax = max_players
		self.players = []
		self.board = Board(width, height)
		self.playerTurnIndex = 0
		self.wipePlayersOnLose = False
		self.gameState = GameState.PreGame
		self.settingAiReplace = False
	
	def getGameStateStr(self):
		if self.gameState == GameState.PreGame:
			return "Pre-Game"
		elif self.gameState == GameState.InGame:
			return "In-Game"
		elif self.gameState == GameState.PostGame:
			return "Post-Game"
		return "Unknown"
	
	def startGame(self):
		self.gameState = GameState.InGame
		self.sendMessageToAll(u"gamebegin:")
		self.sendBoardToAll()
		self.sendMessageToAll(u"turn:%s" % self.players[self.playerTurnIndex].getSymbol())
	
	def makeMove(self, data):
		move = data.split(' ')
		if self.gameState == GameState.InGame and len(move) == 2:
			x = move[0]
			y = move[1]
			if x.isdigit() and int(x) >= 0:
				x = int(x)
			else:
				x = -1
			if y.isdigit() and int(y) >= 0:
				y = int(y)
			else:
				y = -1
			if self.validCoord(x, y):
				if (self.board.board[self.board.getCoordIndex(x, y)] == None):
					self.board.board[self.board.getCoordIndex(x, y)] = self.playerTurnIndex
					playerwinner = self.doBoardActions()
					self.sendBoardToAll()
					if playerwinner is not None:
						self.doPostGame()
						self.sendMessageToAll(u"gamelog:Player %c has won the game!" % self.players[playerwinner].getSymbol())
						self.sendMessageToAll(u"gameover:%s" % self.players[playerwinner].getSymbol())
					else:
						self.selectNextTurn()
					return True
					
		return False
	
	def selectNextTurn(self):
		self.playerTurnIndex += 1
		if self.playerTurnIndex >= self.getPlayerCount():
			self.playerTurnIndex = 0
		while (self.players[self.playerTurnIndex].hasLost()):
			self.playerTurnIndex += 1
			if self.playerTurnIndex >= self.getPlayerCount():
				self.playerTurnIndex = 0
		self.sendMessageToAll(u"turn:%s" % self.players[self.playerTurnIndex].getSymbol())
		if self.players[self.playerTurnIndex].client is None:
			print("AI MOVE PROBLEM 53")
			self.sendMessageToAll(u"info:AI move issue!")
			self.selectNextTurn()
	
	def doPostGame(self):
		self.gameState = GameState.PostGame
		print("Closing game %d!" % self.gameId)
		self.sendMessageToAll(u"postdata:%s" % self.getPostGameReport())
	
	def getPostGameReport(self):
		return "Derpy tried her best.";
	
	def sendMessage(self, client, message):
		if client is not None:
			client.write_message(message)
			return True
		return False
	
	def sendMessageToAll(self, message):
		for player in self.players:
			if player.client is not None:
				try:
					player.client.write_message(message)
				except:
					pass
	
	def sendBoardToAll(self):
		board = ""
		for i in self.board.board:
			if i == None:
				board += '.'
			else:
				board += self.players[int(i)].getSymbol()
		self.sendMessageToAll(u"board:"+str(self.board.getWidth())+','+str(self.board.getHeight())+','+board)
	
	def validCoord(self, x, y):
		if x >= 0 and y >= 0 and x < self.width and y < self.height:
			return True
		return False
	
	def setWipePlayersOnLose(self, wipeOff):
		self.wipePlayersOnLose = wipeOff
	
	def allPlayerDataToString(self):
		if len(self.players) <= 0:
			return None
		data = ""
		for player in self.players:
			data += "%s-%s-%s," % (player.getSymbol(), "D" if player.hasLost() else "A", "Ai" if player.isAi() else "H")
		return data[0:-1]
	
	def addPlayer(self, instance):
		print "game %d %d %d %d %d" % (self.gameId, self.gameState, GameState.PreGame, self.getPlayerCount(), self.playersMax)
		if self.gameState == GameState.PreGame:
			if self.getPlayerCount() < self.playersMax:
				newPlayer = Player(instance, self.getUniqueSymbol(), self.wipePlayersOnLose)
				self.players.append(newPlayer)
				self.sendMessage(instance, u"youare:%s" % newPlayer.getSymbol())
				self.sendMessageToAll(u"joiner:%s" % newPlayer.getSymbol())
				self.sendMessageToAll(u"players:%s" % self.allPlayerDataToString())
				self.sendMessage(instance, u"info:Joined Game!")
				self.sendMessage(instance, u"state:%d,%s" % (self.gameState, self.getGameStateStr()))
				if self.getPlayerCount() == 1:
					self.notifyHostPrivileges()
				print "Player %s joined game" % newPlayer.getSymbol()
			else:
				print "Player Rejected: game is full"
				self.sendMessage(instance, u"joinfail:Game is Full!")
			return
		if self.gameState == GameState.PostGame:
			print "Player Rejected: joined in post-game"
			self.sendMessage(instance, u"joinend:This game has already ended!")
		else:
			print "Player Rejected: Observer"
			self.sendMessage(instance, u"joinfail:Game already in progress!")
	
	def removePlayer(self, playerId):
		self.sendMessageToAll(u"leaver:%s" % self.players[playerId].getSymbol())
		if self.gameState == GameState.PreGame:
			del self.players[playerId]
			if self.closeGameIfEmpty():
				return
			if playerId == 0:
				self.notifyHostPrivileges()
		else:
			self.players[playerId].client = None;
			if self.settingAiReplace == True:
				self.players[playerId].setAi(True)
			else:
				self.players[playerId].setLost()
				if self.wipePlayersOnLose == True:
					self.board.removeIdFromBoard(playerId)
	
	def closeGameIfEmpty(self):
		if self.getPlayerCount() <= 0:
			self.doPostGame()
			return True
		return False
	
	def notifyHostPrivileges(self):
		if self.gameState == GameState.PreGame:
			if self.closeGameIfEmpty():
				return
			if not self.sendMessage(self.players[0].client, u"uhost:You are the new host of this lobby!\nStart the game when ready."):
				self.removePlayer(0)
	
	def getUniqueSymbol(self):
		symbol = None
		while symbol is None:
			symbol = str(unichr(randint(65,90)))#A-Z
			for playerId in range(0, self.getPlayerCount()):
				if self.players[playerId].getSymbol() == symbol:
					symbol = None
					break
		return symbol
	
	def getPlayerIdFromSymbol(self, symbol):
		for playerId in range(0, self.getPlayerCount()):
			if self.players[playerId].getSymbol() == symbol:
				return playerId
		return None
	
	def getPlayerIdFromInstance(self, instance):
		for playerId in range(0, self.getPlayerCount()):
			if self.players[playerId].client == instance:
				return playerId
		return None
	
	def getPlayerSymbolfromId(self, playerId):
		return self.players[playerId].getSymbol()
	
	def doBoardActions(self):
		self.removeNoLiberties()
		return self.detectWinner()
	
	def removeNoLiberties(self):
		checkedStones = [False] * (self.board.getWidth() * self.board.getHeight())
		stringList = []
		for index in range(0, self.board.getWidth() * self.board.getHeight()):
			if checkedStones[index] == False:
				checkedStones[index] = True
				playerId = self.board.board[index]
				if playerId >= 0:
					stoneStringInfo = stoneString, hasLiberties = self.board.getStringAtIndex(index)
					for stoneIndex in stoneString:
						checkedStones[stoneIndex] = True
					if hasLiberties == False:
						stringList.append(stoneStringInfo)
		if len(stringList) > 0:
			if len(stringList) == 1:
				playerId = self.board.getStoneIdAtIndex(stringList[0][0][0])
				if not self.players[playerId].hasLost():
					self.players[playerId].setLost()
					self.sendMessageToAll(u"lost:%c" % self.players[playerId].getSymbol())
					if playerId == self.playerTurnIndex:
						print "Player %c has eliminated themself!" % self.players[playerId].getSymbol()
						self.sendMessageToAll(u"gamelog:Player %c has eliminated themself!" % self.players[playerId].getSymbol())
					else:
						self.players[self.playerTurnIndex].incrementKills()
						print "Player %c has been eliminated!" % self.players[playerId].getSymbol()
						self.sendMessageToAll(u"gamelog:Player %c has been eliminated!" % self.players[playerId].getSymbol())
				self.players[self.playerTurnIndex].incrementStringKills()
				self.board.removeString(stringList[0][0])
			else:
				for stringIndex in range(0, len(stringList)):
					playerId = self.board.getStoneIdAtIndex(stringList[stringIndex][0][0])
					if not playerId == self.playerTurnIndex:
						if not self.players[playerId].hasLost():
							self.sendMessageToAll(u"lost:%c" % self.players[playerId].getSymbol())
							self.players[self.playerTurnIndex].incrementKills()
							print "Player %c has been eliminated!" % self.players[playerId].getSymbol()
							self.sendMessageToAll(u"gamelog:Player %c has been eliminated!" % self.players[playerId].getSymbol())
						self.players[playerId].setLost()
						self.players[self.playerTurnIndex].incrementStringKills()
						self.board.removeString(stringList[stringIndex][0])
			for playerId in range(0, self.getPlayerCount()):
				if self.players[playerId].hasLost() and not self.players[playerId].isWipedOffBoard():
					self.board.removeIdFromBoard(playerId)
	
	def getPlayerCount(self):
		return len(self.players)
	
	#Returns a tuple where
	#index 0: number of players remaining
	#index 1: list of remaining player ID's
	def playersRemaining(self):
		remainingPlayerCount = 0
		playerList = []
		for playerId in range(0, self.getPlayerCount()):
			if not self.players[playerId].hasLost():
				remainingPlayerCount += 1
				playerList.append(playerId)
		return (remainingPlayerCount, playerList)
	
	#Returns None if no winner, otherwise player ID
	def detectWinner(self):
		remainingPlayerCount, players = self.playersRemaining()
		if remainingPlayerCount == 0:
			return self.playerTurnIndex
		elif remainingPlayerCount == 1:
			return players[0]
		return None
		
		
if __name__ == '__main__':
	print "test compile success?"
