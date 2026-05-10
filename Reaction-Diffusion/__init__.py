bl_info = {
    "name": "Reaction Diffusion addon",
    "author": "Kroslak",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > RD",
    "description": "Reaction-diffusion meshes in 2D or 3D",
    "category": "Add Mesh",
}

import bpy

from . import deps
from . import properties
from . import operators
from . import panels

classes = (
    deps.RD_OT_install_dependencies,
    properties.RDSettings,
    operators.RD_OT_generate,
    operators.RD_OT_generate_preview,
    operators.RD_OT_generate_preview_3d,
    panels.RD_PT_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rd_settings = bpy.props.PointerProperty(type=properties.RDSettings)


def unregister():
    if hasattr(bpy.types.Scene, "rd_settings"):
        del bpy.types.Scene.rd_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
