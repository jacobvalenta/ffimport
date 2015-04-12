# ffimport [v0.4]


ffimport is a <i>Blender 3D 2.7x</i> import/export plugin. With it, it brings the power to import extracted game files from <i>Final Fantasy VII</i> and allows the models to be easily edited and animated. Options allow for selective importing of components, such as wireframe, materials, textures and texture coordinates.

To import a full model (including bones), import a .hrc file. This file points to other files (polygon & textures) and will automaticly assemble the model and skelton structure. To import the animation data for the skeleton, import a .a file.

## Installation

Copy or symlink `io_scene_ff7` to `$BlenderFolder/2.65/Scripts/addons/`. Launch Blender, open user preferences, go to the addons tab, find 'Final Fantasy VII Format' and enable it.

