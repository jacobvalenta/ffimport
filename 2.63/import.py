import bpy
import struct

def load_p(filepath, debug):
    f = open(filepath, 'rb')

    header = f.read(64)
    runtimeData = f.read(64) # usually not read, but may be used in export.
    header = struct.unpack('llllllllllllllll', header) # convert binary header to integers

    version = header[0]
    vertexType = header[2]
    numVertices = header[3]
    numNormals = header[4]
    numUnknown1 = header[5]
    numTexCoords = header[6]
    numVertexColors = header[7]
    numEdges = header[8]
    numUnknown2 = header[9]
    numUnknown3 = header[10]
    numPolygons = header[11]
    numHundreds = header[12]
    numGroups = header[13]
    numBoundingBoxes = header[14]
    normIndexTableFlag = header[15]

    if debug == True:
        print('Verticies: \t', numVertices)
        print('Edges: \t\t', numEdges)
        print('Faces: \t\t', numPolygons)

    f.close()

def start_import(context, filepath, debug):
    #first thing first is to determin the type of file we are working with
    filepath = filepath.replace('\\', '/')
    filename = filepath.split('/')[-1]
    filetype = filename.split('.')[-1]

    if debug == True:
        print(filename)
        print(filetype)

    #which ever filetype we are using, call the appropriate function
    if filetype == 'p':
        load_p(filepath, debug)

    return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator



#main class to setup import window for blender
class ffimport(Operator, ImportHelper):
    '''Import Final Fatnasy files (.hrc .rsd .p .tex .a)'''
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import"

    filename_ext = ".p" #Not quite sure how blender uses this

    filter_glob = StringProperty(
            default="*.p",
            options={'HIDDEN'},
            )

    # Create the User interface 
    debug_s = BoolProperty(
            name="Debug",
            description="Toggels debug info sent to the console.",
            default=True,
            )

    def execute(self, context):
        return start_import(context, self.filepath, self.debug_s)


# Adds a listing in the Import menu
def menu_func_import(self, context):
    self.layout.operator(ffimport.bl_idname, text="Final Fantasy")


def register():
    bpy.utils.register_class(ffimport)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ffimport)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_test.some_data('INVOKE_DEFAULT')
