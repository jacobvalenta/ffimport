import bmp
import tex

texFile = tex.TEX('../Examples/aabc.tex')
bmpFile = bmp.BMP()
bmpFile.data(texFile.data)
bmpFile.save('export.bmp')