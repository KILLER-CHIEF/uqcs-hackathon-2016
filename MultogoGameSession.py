from MultogoBoard import Board
from MultogoPlayer import Player
from random import randint

class GameState(object):
	PreGame = 0
	InGame = 1
	PostGame = 2

class GameSession(object):
	#
	
	def __init__(self, width, height, playerLimit):
		self.board = Board(width, height)
		self.players = []
		self.playerTurnIndex = 0
		self.wipePlayersOnLose = False
		self.gameState = GameState.PreGame
		self.playerLimit = playerLimit
	
	def setWipePlayersOnLose(self, wipeOff):
		self.wipePlayersOnLose = wipeOff
	
	def addPlayer(self, symbol):
		if self.gameState == GameState.PostGame:
			print "Player joined in post-game"
			return
		if self.gameState == GameState.PreGame and self.playerCount() < self.playerLimit:
			self.players.append(Player(symbol, self.wipePlayersOnLose))
		else:
			print "Player Observer"
	
	def getUniqueSymbol(self):
		symbol = None
		while symbol is None:
			symbol = str(unichr(randint(65,90)))#A-Z
			for playerId in range(0, self.playerCount()):
				if self.players[playerId].getSymbol() == symbol:
					symbol = None
					break
		return symbol
	
	def getPlayerIdFromSymbol(self, symbol):
		for playerId in range(0, self.playerCount()):
			if self.players[playerId].getSymbol() == symbol:
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
			for playerId in range(0, self.playerCount()):
				if self.players[playerId].hasLost() and not self.players[playerId].isWipedOffBoard():
					removeIdFromBoard(playerId)
	
	def playerCount(self):
		return len(self.players)
	
	#Returns a tuple where
	#index 0: number of players remaining
	#index 1: list of remaining player ID's
	def playersRemaining(self):
		remainingPlayerCount = 0
		playerList = []
		for playerId in range(0, self.playerCount()):
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