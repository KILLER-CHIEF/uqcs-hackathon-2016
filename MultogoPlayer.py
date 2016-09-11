

class Player(object):
	#
	
	def __init__(self, instance, symbol, wipePlayersOnLose):
		self.client = instance
		self.symbol = symbol
		self.ai = False
		self.lost = False
		self.wipedOffBoard = not wipePlayersOnLose
		self.moveCount = 0
		self.kills = 0
		self.stringKills = 0
	
	def getSymbol(self):
		return self.symbol
	
	def setSymbol(self, symbol):
		self.symbol = symbol
	
	def isAi(self, ai):
		return self.ai
	
	def setAi(self, ai):
		self.ai = ai
		if self.ai == True:
			self.client = None
	
	def hasLost(self):
		return self.lost
	
	def setLost(self):
		self.lost = True
	
	def isWipedOffBoard(self):
		return self.wipedOffBoard
	
	def setWipedOffBoard(self):
		self.wipedOffBoard = True
	
	def incrementMoveCount(self):
		self.moveCount += 1
	
	def incrementKills(self):
		self.kills += 1
	
	def incrementStringKills(self):
		self.stringKills += 1
	
	
if __name__ == '__main__':
	print "test compile success?"