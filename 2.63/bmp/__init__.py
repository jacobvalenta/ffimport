class Bmp():
	'''Easily creates bmp files given pixel data'''
	def __init__(self):
		pass

	def data(self, pixels):
		'''Sets the pixel data for the bitmap'''
		pass

	def save(self, filename):
		'''Saves the bitmap the the filename provided (.bmp)'''
		pass

if __name__ == '__main__':
	image = Bmp()
	image.data((
				(0, 0, 0), (1, 0, 0), (1, 1, 0),
				(0, 1, 1), (0, 0, 1), (1, 1, 1)
				))
	image.save('myPicture')