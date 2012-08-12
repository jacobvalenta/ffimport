import bpy
import struct
import os.path
from mathutils import Vector
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

def load_p(filepath, debug, wireframe = False, loadMaterials = True):
    f = open(filepath, 'rb')

    header = struct.unpack('llllllllllllllll', f.read(64)) #convert binary headers to integers
    runtimeData = f.read(64) # usually not read, but may be used in export.

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
        print('\nLoading Polygon Model\n')
        print('Verticies: \t', numVertices)
        print('Edges: \t\t', numEdges)
        print('Faces: \t\t', numPolygons)
        print('NumUnknown: \t', numUnknown1)

    # Loaded in all the parts of the file. Taken from code posted by Aali :)
    vertices =   [list(struct.unpack("fff",                       f.read(0xC)))  for i in range(numVertices)]
    normals =    [struct.unpack("fff",                       f.read(0xC))  for i in range(numNormals)]
    unknown1 =   [struct.unpack("fff",                       f.read(0xC))  for i in range(numUnknown1)]
    texcoords =  [struct.unpack("ff",                        f.read(0x8))  for i in range(numTexCoords)]
    vertcolors = [struct.unpack("I",                         f.read(0x4))  for i in range(numVertexColors)]
    polycolors = [struct.unpack("BBBB",                         f.read(0x4))  for i in range(numPolygons)]
    edges =      [list(struct.unpack("hh",                         f.read(0x4)))  for i in range(numEdges)]
    polygonsTmp =   [struct.unpack("HHHHHHHHHHI",               f.read(0x18)) for i in range(numPolygons)]
    unknown2 =   [struct.unpack("HHHHHHHHHHI",               f.read(0x18)) for i in range(numUnknown2)]
    unknown3 =   [struct.unpack("BBB",                       f.read(0x3))  for i in range(numUnknown3)]
    hundreds =   [struct.unpack("IIIIIIIIIIIIIIIIIIIIIIIII", f.read(0x64)) for i in range(numHundreds)]
    groups =     [struct.unpack("IIIIIIIIIIIIII",            f.read(0x38)) for i in range(numGroups)]
    boundingboxes = [struct.unpack("IIIIIII",                   f.read(0x1C)) for i in range(numBoundingBoxes)]    

    f.close() #We're done here, move along

    #grab usable data from polys
    polygons = []
    for i in polygonsTmp:
        polygons.append([i[1], i[2], i[3]])


    #Blender materials create now, applied within poly groups
    #enumerate materials
    if loadMaterials == True:
        if debug == True:
            print('Generating Materials')
        materials = []
        internalMaterials = []

        for i in polycolors:
            if i not in materials:
                materials.append(i)

        print ('done')

        #create materials
        for material in materials:
            materialName = '%x%x%x%x' % material

            if debug == True:
                print('Creating Material:', materialName)


            blenderMaterial = bpy.data.materials.new(materialName)

            red = (material[2] / 255)
            green = (material[1] / 255)
            blue = (material[0] / 255)
            alpha = (material[3] /255)

            blenderMaterial.diffuse_color = (red, green, blue)
            blenderMaterial.diffuse_shader = 'LAMBERT'
            blenderMaterial.diffuse_intensity = 1.0
            blenderMaterial.specular_color = (1, 1, 1)
            blenderMaterial.specular_shader = 'COOKTORR'
            blenderMaterial.specular_intensity = 0.0
            blenderMaterial.alpha = (alpha)
            blenderMaterial.ambient = 1
            internalMaterials.append(blenderMaterial)

    #parse da groups ze correct way
    for i, group in enumerate(groups):
        if debug == True:
            print('\nLoading group:\n')
        polyOffset = group[1]
        polyRange = group[2]
        vertexOffset = group[3]
        vertexRange = group[4]
        edgeOffset = group[5]
        edgeRange = group[6]
        textureOffset = group[11]
        isTextured = bool(group[12])
        textureRange = group[13]

        if debug == True:
            print('Vertex Offset: \t', vertexOffset)
            print('Vertex Range: \t', vertexRange)
            print('Edge Offset: \t', edgeOffset)
            print('Edge Range: \t', edgeRange)
            print('Polygon Offset: ', polyOffset)
            print('Poly Range: \t', polyRange)
            print('Textured: \t', isTextured)
            print('Texture Offset: ', textureOffset)
            print('Texture Range: \t', textureRange)

        #generate verts and faces for this group
        groupVertices = vertices[vertexOffset:(vertexRange + vertexOffset)]
        groupEdges = edges[edgeOffset: (edgeRange + edgeOffset)]
        groupPolygons = polygons[polyOffset : (polyRange+ polyOffset)]
        groupPolyColors = polycolors[polyOffset : (polyRange + polyOffset)]

        #create an object out of what we just got
        ffMesh = bpy.data.meshes.new('ffimport' + str(i))
        if wireframe == True:
            ffMesh.from_pydata(groupVertices, groupEdges)
        else:
            ffMesh.from_pydata(groupVertices, [], groupPolygons)
        ffMesh.update()
        ffObject = bpy.data.objects.new('ffimport' + str(i), ffMesh)
        bpy.context.scene.objects.link(ffObject)


        # Load materials for this group
        #This was coding in close proximity to mountindew and asprin
        if loadMaterials == True:
            for ni, material in enumerate(materials):
                materialName = '%x%x%x%x' % material
                if debug == True:
                    print('Material and vertex group name:', materialName)
                polyGroup = []
                vertexGroup = []
                for i, polymat in enumerate(groupPolyColors):
                    if polymat == material:
                        polyGroup.append(i)
                for poly in polyGroup:
                    for vertex in groupPolygons[poly]:
                        if vertex not in vertexGroup:
                            vertexGroup.append(vertex)
                weightedGroup = [] #Weights not nessisary, clean up later
                for vertex in vertexGroup:
                    weightedGroup.append((vertex, 1.0))
                group = ffObject.vertex_groups.new(materialName)
                for vertex, weight in weightedGroup:
                    group.add([vertex], weight, 'REPLACE')

                #assign material to group; it works and I have no idea why
                #TODO :| just found bpy.data.objects[].active_material_index....

                bpy.context.scene.objects.active = ffObject
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.vertex_group_set_active(group=materialName)
                bpy.ops.object.vertex_group_select()
                bpy.ops.object.material_slot_add()
                bpy.context.object.material_slots[-1].material = internalMaterials[ni]
                bpy.ops.object.material_slot_assign()
                bpy.ops.object.mode_set(mode='OBJECT')

        #load UV data
        #I have been searching for 8 hours... no luck

def load_hrc(filepath, debug, wireframe, loadMaterials):
    if debug == True:
        print('\nReading Skeleton File\n')

    f = open(filepath, 'r')

    #Read header info
    header = [f.readline() for i in range(3)]
    SkeletonName = header[1].strip('\n')[10:]
    numberBones = int(header[2].strip('\n')[7:])
    if debug == True:
        print('Importing:', SkeletonName)
        print('Number of Bones:', numberBones)

    bones = [[f.readline().strip('\n') for a in range(5)] for i in range(numberBones)]
    f.close()

    #create armature
    bpy.ops.object.add(type="ARMATURE", enter_editmode=True)
    object = bpy.context.object
    object.name = SkeletonName
    armature = object.data
    armature.name = SkeletonName

    #create root bone, which is the orgin for all bones of a model
    bpy.ops.object.mode_set(mode='EDIT')
    bone = armature.edit_bones.new("root")
    bone.head = Vector((0.0, 1.0, 0.0))
    bone.tail = Vector((0.0, 0.0, 0.0))


    for dataBone in bones:
        name = dataBone[1]
        parent = dataBone[2]
        length = float(dataBone[3])
        resources = dataBone[4].split(' ')[0]

        #add bone to armature
        bone = armature.edit_bones.new(name)
        parentBone = armature.edit_bones[parent]
        bone.parent =  parentBone
        bone.head = parentBone.tail
        bone.tail = Vector((0.0, parentBone.tail[1] + length, 0.0))

        #link models to this bone

def load_tex(filepath, debug):
    if debug == True:
        print('\nimporting texture')

    f = open(filepath, 'rb')

    # :( This is Going to be a HUGE function

    #load header
    header = list(struct.unpack('lllllllllllllllllllllllllll', f.read(108)))

    #Wait for it....

    colorKeyFlag = bool(header[2])
    numberOfPallets = header[12]
    colorsPerPallet = header[13]
    bitDepth = header[14]
    imageWidth = header[15]
    imageHeight = header[16]
    palletFlag = bool(header[19])
    bitsPerIndex = header[20]
    palletSize = header[22]

    if debug == True:
        print('Version:\t\t\t', header[0])
        print('Color key flag:\t\t\t', bool(header[2]))
        print('D3D Minimum Bit depth:\t\t', header[5])
        print('Maximum bit depth:\t\t', header[6])
        print('minimum alpha bits:\t\t', header[7])
        print('Maximume alpha bits:\t\t', header[8])
        print('Minimun bits per pixel:\t\t', header[9])
        print('Maximum bits per pixel:\t\t', header[10])
        print('Number of Pallets:\t\t', header[12])
        #There's more...
        print('Number of Colors Per Pallet:\t', header[13])
        print('Bit Depth:', header[14])
        print('Image Width:', header[15])
        print('Image Height:', header[16])
        print('Pitch: ', header[17])
        #so help me God...


    bmpHeader = b'\x42\x4d'
    bmpHeader += b'\x00\x00\x00\x00'
    bmpHeader += b'\x00\x00'
    bmpHeader += b'\x00\x00'
    bmpHeader += b'\x36\x00\x00\x00'

    f.close()

def load_rsd(filepath, debug, wireframe = False, loadMaterials = True):
    if debug == True:
        print('\nImporting Resource Data file\n')
    f = open(filepath, 'r')
    lines = f.readlines()
    textureList = []
    for i,c in enumerate(lines):
        if i == 0:
            if c[:4] != '@RSD':
                print('File is not an RSD file, continuing anyways, no gaurentees')
        else:
            try:
                if c[:1] == '#':
                    continue #this just ignores comments
                if c[:3] == 'PLY':
                    fileToLoad = c[4:8].lower()
                    if debug == True:
                        print('P file to load:', fileToLoad) # discover which .p file to use
                if c[:5] == 'NTEX=':
                    numTextures = int(c[5:].strip('\r\n'))
                    if debug == True:
                        print('Textures associated:', numTextures) # find the number of textures used
                if c[:4] == 'TEX[':
                    textureList.append(c[7:11].lower())
            except:
                continue
    f.close

    filename = filepath.split('/')[-1]
    currentDirectory = filepath[:-1 * (len(filename))]

    #load textures
    for texture in textureList:
        if os.path.isfile(currentDirectory + texture):
            load_tex(currentDirectory + texture, debug)
        elif os.path.isfile(currentDirectory + texture + '.tex'):
            load_tex(currentDirectory + texture + '.tex', debug)
        else:
            print("Could not find texture file")


    #Load Polygon files
    if os.path.isfile(currentDirectory + fileToLoad):
        load_p(currentDirectory + fileToLoad, debug, wireframe, loadMaterials)
    elif os.path.isfile(currentDirectory + fileToLoad + '.p'):
        load_p(currentDirectory + fileToLoad + '.p', debug, wireframe, loadMaterials)
    else:
        print('The polygon file linked to this file could not be found.')

def start_import(context, filepath, debug, wireframe, loadMaterials):
    if debug == True:
        print('Starting ffimport')
    #first thing first is to determin the type of file we are working with
    filepath = filepath.replace('\\', '/') #just in case we are on a windows machine
    filename = filepath.split('/')[-1]
    filetype = filename.split('.')[-1]

    #which ever filetype we are using, call the appropriate function
    if filetype == 'p':
        load_p(filepath, debug, wireframe, loadMaterials)
    elif filetype == 'rsd':
        load_rsd(filepath, debug, wireframe, loadMaterials)
    elif filetype == 'tex':
        load_tex(filepath, debug)
    elif filetype == 'hrc':
        load_hrc(filepath, debug, wireframe, loadMaterials)

    return {'FINISHED'}


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
    loadMaterials = BoolProperty(name="Load Materials", description="Loads material data associated with polygons", default=True)

    def execute(self, context):
        return start_import(context, self.filepath, self.debug_s, self.wireframe, self.loadMaterials)

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
