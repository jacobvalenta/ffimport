this library is something I created to more easily, and cleanly handle BMP files.

This allows you to load a BMP file or create one.

use like this:

>>>from bmp import bmp
>>>
>>>image = bmp()
>>>image.data = ([[(0, 0, 0), (1, 0, 0)],   #This a 2x2 BMP, given 0.0 - 1.0 values
>>>               [(0, 1, 0), (0, 0, 1)]])
>>>
>>>image.save('myPicture') #saves to myPicture.bmp

and this is later implemented with tex files, for easy interpretation.