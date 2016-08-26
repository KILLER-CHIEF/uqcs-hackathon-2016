



class board(object):
	
	#Note: Stone ID's
	# -2 == Unknown / Invalid / Error
	# -1 == Space / No Stone
	#  0 == Player 0
	#  1 == Player 1
	#  . == Player .
	#  x == Player x
	
	def __init__(self, width, height):
		self.board = [-1] * (width * height)
		self.width = width
		self.height = height
	
	#Returns type int index
	def GetCoordIndex(self, x, y):
		return x + (y * self.width)
	
	#Returns coordinate in tupple (x, y)
	def GetIndexCoord(self, index):
		return (index % self.width, index // self.height)
	
	#Returns Stone ID at that index
	def GetStoneIdAtIndex(self, index):
		if (index < 0 or index >= self.width * self.height):
			return -2
		return self.board[index]
	
	#Returns Stone ID at that coordinate
	def GetStoneIdAtCoord(self, x, y):
		if (x < 0 or x >= self.width):
			return -2
		if (y < 0 or y >= self.height):
			return -2
		return self.board[GetCoordIndex(x, y)]
	
	
	#Returns tupple where
	#index 0 is list of index-locations of Stones
	#index 1 is if it has liberties
	def GetStringAtIndex(self, index):
		stringStoneIndexs = []
		hasLiberty = False
		stoneId = GetStoneIdAtIndex(index)
		uncheckedStoneList = [index]
		while len(uncheckedStoneList) > 0:
			checkingStoneIndex = uncheckedStoneList.pop(0)
			stringStoneIndexs.append(checkingStoneIndex)
			x, y = GetIndexCoord(checkingStoneIndex)
			for loop4Times in range(0,4):
				i = x
				j = y - 1
				if loop4Times == 1:
					i = x - 1
					j = y
				elif loop4Times == 2:
					i = x
					j = y + 1
				elif loop4Times == 3:
					i = x + 1
					j = y
				checkingStoneIndex = GetCoordIndex(i, j)
				if (j >= 0 and i >= 0 and j < self.height and i < self.width and checkingStoneIndex not in uncheckedStoneList and checkingStoneIndex not in stringStoneIndexs):
					tempIndexId = self.board[checkingStoneIndex]
					if tempIndexId == -1:
						hasLiberty = true
					elif tempIndexId == id:
						uncheckedStoneList.append(GetCoordIndex(i, j))
		return (stringStoneIndexs, hasLiberty)
	
	
	
if __name__ == '__main__':
	print "test compile"