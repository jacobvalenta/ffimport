import struct

def load(context, filepath, debug):
	'''Fuction to initiate the loading process for files. Used to establish file type and which load fuction that should be used.'''
	#This function will receive mroe parameters as I add functionality back to 2.64
	global debug #looking back on it, I dont know why I even added this... maybe I did this so I didnt have to pass it to the other load functions
	debug = debug

	#disect the filepath
    filepath = filepath.replace('\\', '/') #just in case we are on a windows machine
    filename = filepath.split('/')[-1] #gives us something that looks like 'hello.txt'
    filetype = filename.split('.')[-1] #gives us something that looks like 'txt'

    #elementary filetype testing
    if filetype == 'p':
    	load_p(filepath)
    #will add more when I add a bit more functionality

    #Secondary filetype tests: battle models which do not have file extentions

    #End secondary

	return {'FINISHED'}

def debug(message):
	'''Just a simple debug handler'''
	if debug == True:
		print(message) #makes it so I dont have to keep typing if debug == True:

def load_p(filepath):
	'''A function for importing polygon files from Final Fantasy VII'''
	debug('Starting load_p()')

	f = open(filepath)

	header = struct.unpack('lllllllllllll', f.read(64)) #convert binary headers to integers

	data = {'VERSION': header[0]
			'VERTEX TYPE': header[2]}


	f.close()

	pass

def load_rsd():
	'''A function for importing resource files from Final Fantasy VII'''
	pass

def load_hrc():
	'''A function for importing heiarcy files from Final Fantasy VII'''
	pass

def load_tex():
	'''A function for importing texture files from Final Fantasy VII'''
	pass

def load_a():
	'''A function for importing animation files from Final Fantasy VII'''
	pass