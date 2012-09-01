from struct import pack, unpack

class TEX():
	'''A class for easily importing and exporting TEX files from final fantasy VII.'''
	def __init__(self, filepath = None):
		self.width = 0
		self.height = 0
		self.filepath = filepath
		if self.filepath != None:
			self.load(self.filepath)

	def load(self, filename):
		'''Load a texture file in. The pixel data can be accessed through self.data'''
		self.file = open(filename, 'rb')

		self.header = unpack('lllllllllllllllllllllllllllllllllllllllllllllllllllllllllll', self.file.read(236))

		self.pallets = self.header[12]
		self.colorsPerPallet = self.header[13]
		self.bitDepth = self.header[14]
		self.width = self.header[15]
		self.height = self.header[16]
		self.redBitmask = self.header[31]
		self.greenBitmask = self.header[32]
		self.blueBitmask = self.header[33]
		self.alphaBitmask = self.header[34]

		self.pallet = []
		if self.pallets > 0:
			for i in range(self.colorsPerPallet):
				self.pallet.append((unpack('B', self.file.read(1))[0]/255, unpack('B', self.file.read(1))[0]/255, unpack('B', self.file.read(1))[0]/255, unpack('B', self.file.read(1))[0]/255))
		self.file.close()

		self.data = self.pallet

if __name__ == '__main__':
	myImage = TEX()
	myImage.load('aabb.tex')
	print(myImage.data)