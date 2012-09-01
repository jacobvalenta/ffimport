from struct import unpack, pack

class BitmapError(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)


class BMP():
	'''Easily creates BMP files given pixel data; Warning, I am fragile. Do not try using me as a real BMP library'''
	def __init__(self):
		#add defuatls
		self.width = 0
		self.height = 0

	def data(self, pixels):
		'''Sets the pixel data for the bitmap'''
		# TODO verify data
		self.height = len(pixels)
		self.width = len(pixels[0])
		self.data = pixels

	def save(self, filename):
		'''Saves the bitmap to the filename provided (.bmp)'''

		self.paddingBytes = (self.width * 2) % 4
		self.arrayLength = ((self.width * 2) + self.paddingBytes) * self.height
		self.fileLength = 122 + self.arrayLength

		#construct BMP header
		self.BMPHeader = pack('=bblll', 66, 77, self.fileLength, 0, 122)
		self.DIBHeader = pack('=lllhhlllllllllllqqqqqq', 108, self.width, self.height, 1, 16, 3, self.arrayLength, 2835, 2835, 0, 0, 240, 15, 61440, 3840, 1466527264, 0, 0, 0, 0, 0, 0)
		self.bitmapData = b''

		for row in reversed(self.data):
			for pixel in row:
				self.red = (round(pixel[0] * 15) * 4096)
				self.green = (round(pixel[1] * 15) * 256)
				self.blue = (round(pixel[2] * 15) * 16)
				try:
					self.alpha = round(pixel[3] * 15)	#This just makes alpha optional.
				except:
					self.alpha = 15 					#Otherwise, full opacity.
				self.bitmapData += pack('>H', self.red + self.green + self.blue + self.alpha)
			self.bitmapData += pack('b', 0) * self.paddingBytes

		self.file = open(filename, 'wb')
		self.file.write(self.BMPHeader + self.DIBHeader + self.bitmapData)
		self.file.close()

	def load(self, filename):
		'''Loads Bitmap data from specified file'''
		self.f = open(filename, 'rb')

		self.f.close() 

if __name__ == '__main__':
	image = BMP()
	# image.data((
	# 			((0, 0, 0, 0), (1, 0, 0, 0.5), (1, 1, 0, 0.5)),
	# 			((0, 1, 1, 0), (0, 0, 1, 0.5), (1, 1, 1, 1))
	# 			))
	image.data((
				((0.0, 0.0, 0.0, 0.0),),
				((0.06, 0.06, 0.06, 1.0),),
				((0.25, 0.125, 0.06, 0.99),)
				))
	image.save('myPicture.bmp')