import bpy
import struct

def load_p(filepath, debug, wireframe):
    f = open(filepath, 'rb')

    header = f.read(64)
    runtimeData = f.read(64) # usually not read, but may be used in export.
    header = struct.unpack('llllllllllllllll', header) # convert binary header to integers

    #Break the header into variables
    version = header[0]
    vertexType = header[2]
    numVertices = header[3]
    numNormals = header[4]
    numUnknown1 = header[5]
    numTexCoords = header[6]
    numVertexColors = header[7]
    numEdges = header[8]
    numUnknown2 = header[10]
    numUnknown3 = header[11]
    numPolygons = header[9]
    numHundreds = header[12]
    numGroups = header[13]
    numBoundingBoxes = header[14]
    normIndexTableFlag = header[15]

    if debug == True:
        print('Verticies: \t', numVertices)
        print('Edges: \t\t', numEdges)
        print('Faces: \t\t', numPolygons)
        print('NumUnknown: ', numUnknown1)

    # Load Vertices
    vertices = []
    for i in range(numVertices):
        # for the number of vertices, read float data for X, Y and Z and add them to the vertices list.
        vertex = list(struct.unpack('fff', f.read(12)))
        if debug == True:
            print(vertex)
        vertices.append(vertex)

    #Load Edges
    edges = []
    f.seek( 128 + (12 * numVertices) + (12 * numNormals) + (12 * numUnknown1) + (8 * numTexCoords) + (4 * numVertexColors) + (4 * numPolygons))
    for i in range(numEdges):
        edge = list(struct.unpack('hh', f.read(4)))
        if debug == True:
            print(edge)
        edges.append(edge)

    # Load Faces
    polys = []
    for i in range(numPolygons):
        poly = list(struct.unpack('hhhhhhhhhhl', f.read(24)))
        poly = [poly[1], poly[2], poly[3]]
        if debug == True:
            print(poly)
        polys.append(poly)

    if wireframe == True:
        create_mesh('ffimport', vertices, edges)
    else:
        create_mesh('ffimport', vertices, [], polys)

    f.close()

def create_mesh(name, vertices = [], edges=[], faces=[]):
    importedMesh = bpy.data.meshes.new('name')
    importedMesh.from_pydata(vertices, edges, faces)
    importedMesh.update()

    importedObject = bpy.data.objects.new(name, importedMesh)
    bpy.context.scene.objects.link(importedObject)

def start_import(context, filepath, debug, wireframe):
    #first thing first is to determin the type of file we are working with
    filepath = filepath.replace('\\', '/')
    filename = filepath.split('/')[-1]
    filetype = filename.split('.')[-1]

    if debug == True:
        print(filename)
        print(filetype)

    #which ever filetype we are using, call the appropriate function
    if filetype == 'p':
        load_p(filepath, debug, wireframe)

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
            default="*.p;*.hrc;*.tex;*.rsd;*.a", # Took a while to find, but use a ; to seperate file types :)
            options={'HIDDEN'}
            )

    # Create the User interface 
    debug_s = BoolProperty(name="Debug", description="Toggels debug info sent to the console.", default=True)
    wireframe = BoolProperty(name="Wireframe", description="Loads only vertices and edges", default= False)

    def execute(self, context):
        return start_import(context, self.filepath, self.debug_s, self.wireframe)


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
