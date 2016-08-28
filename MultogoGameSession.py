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
	
	def makeMove(self, data):
		move = data.split(' ')
		if len(move) == 2:
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
			if validCoord(x, y):
				if (self.board[self.board.getCoordIndex(x, y)] == None):
					self.board[self.board.getCoordIndex(x, y)] = self.playerTurnIndex
					return True
		return False
	
	def validCoord(self, x, y):
		if x >= 0 and y >= 0 and x < self.width and y < self.height:
			return True
		return False
	
	def setWipePlayersOnLose(self, wipeOff):
		self.wipePlayersOnLose = wipeOff
	
	def addPlayer(self, instance):
		if self.gameState == GameState.PreGame and self.getPlayerCount() < self.playersMax:
			self.players.append(Player(instance, self.getUniqueSymbol(), self.wipePlayersOnLose))
			instance.write_message(u"info:Joined Game!")
			return
		if self.gameState == GameState.PostGame:
			print "Player joined in post-game"
		else:
			print "Player Observer"
		instance.write_message(u"invalid:Failed to Join!")
	
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
	
	def removeNoLiberties(self):
		checkedStones = [False] * (self.board.getWidth() * self.board.getHeight())
		stringList = []
		for index in range(0, self.board.getWidth() * self.board.getHeight()):
			if checkedStones[index] == False:
				checkedStones[index] = True
				playerId = self.board[index]
				if playerId >= 0:
					stoneStringInfo = stoneString, hasLiberties = self.board.getStringAtIndex(index)
					for stoneIndex in stoneString:
						checkedStones[stoneIndex] = True
					if hasLiberties == False:
						stringList.append(stoneStringInfo)
		if len(stringList) > 0:
			if len(stringList) == 1:
				playerId = stringList[0][0][0]
				if not self.players[playerId].hasLost():
					self.players[playerId].setLost()
					if playerId == self.playerTurnIndex:
						print "Player %c has eliminated themself!" % self.players[playerId].getSymbol()
					else:
						self.players[self.playerTurnIndex].incrementKills()
						print "Player %c has been eliminated!" % self.players[playerId].getSymbol()
				self.players[self.playerTurnIndex].incrementStringKills()
				self.board.removeString(stringList[0][0])
			else:
				for stringIndex in range(0, len(stringList)):
					playerId = stringList[stringIndex][0][0]
					if not playerId == self.playerTurnIndex:
						if not self.players[playerId].hasLost():
							self.players[self.playerTurnIndex].incrementKills()
							print "Player %c has been eliminated!" % self.players[playerId].getSymbol()
						self.players[playerId].setLost()
						self.players[self.playerTurnIndex].incrementStringKills()
						self.board.removeString(stringList[stringIndex][0])
			for playerId in range(0, self.getPlayerCount()):
				if self.players[playerId].hasLost() and not self.players[playerId].isWipedOffBoard():
					removeIdFromBoard(playerId)
	
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
		remainingPlayerCount, players = playersRemaining()
		if remainingPlayerCount == 0:
			return self.playerTurnIndex
		elif remainingPlayerCount == 1:
			return players[0]
		return None
		
		
if __name__ == '__main__':
	print "test compile success?"