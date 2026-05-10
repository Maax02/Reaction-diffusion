import bpy

from .deps import are_dependencies_installed


class RD_PT_panel(bpy.types.Panel):
    bl_label = "Reaction Diffusion"
    bl_idname = "RD_PT_panel_simple"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RD"

    def draw(self, context):
        layout = self.layout
        s = context.scene.rd_settings

        if are_dependencies_installed():
            layout.label(text="Dependencies installed", icon='CHECKMARK')
        else:
            layout.label(text="Dependencies missing", icon='ERROR')
            layout.operator("rd.install_dependencies", icon='CONSOLE')

        col = layout.column(align=True)
        col.prop(s, "mode")
        col.prop(s, "model")
        col.prop(s, "field_mode")

        if s.mode == '2D' and s.model == 'GRAY_SCOTT':
            col.prop(s, "gray_scott_2d_preset")

        elif s.mode == '3D' and s.model == 'GRAY_SCOTT':
            col.prop(s, "gray_scott_3d_preset")

        elif s.mode == '2D' and s.model == 'BRUSSELATOR':
            col.prop(s, "brusselator_2d_preset")

        elif s.mode == '3D' and s.model == 'BRUSSELATOR':
            col.prop(s, "brusselator_3d_preset")

        elif s.mode == '2D' and s.model == 'FITZHUGH_NAGUMO':
            col.prop(s, "fh_2d_preset")

        elif s.mode == '3D' and s.model == 'FITZHUGH_NAGUMO':
            col.prop(s, "fh_3d_preset")

        layout.separator()

        if s.mode == '2D':
            col = layout.column(align=True)
            col.label(text="2D Grid / Steps:")
            col.prop(s, "size")
            col.prop(s, "steps")
            col.prop(s, "perturb_2d")
        else:
            col = layout.column(align=True)
            col.label(text="3D Volume / Steps:")
            col.prop(s, "size_3d")
            col.prop(s, "steps")
            col.prop(s, "perturb_3d")
            col.prop(s, "iso_level")


        layout.separator()

        col = layout.column(align=True)
        col.label(text="Constants:")
        col.prop(s, "Du")
        col.prop(s, "Dv")

        if s.model == 'GRAY_SCOTT':
            col.prop(s, "F")
            col.prop(s, "k")
            col.prop(s, "do_clamp")
        elif s.model == 'BRUSSELATOR':
            col.prop(s, "A")
            col.prop(s, "B")
            col.prop(s, "dt")
            col.prop(s, "noise")
        elif s.model == 'FITZHUGH_NAGUMO':
            col.prop(s, "fh_a")
            col.prop(s, "fh_b")
            col.prop(s, "fh_eps")
            col.prop(s, "dt")
            col.prop(s, "noise")
            col.prop(s, "fh_strength")
            if s.mode == '2D':
                col.prop(s, "fh_init_mode")
            elif s.mode == '3D':
                col.prop(s, "fh_num_sparks")
        

        layout.separator()

        col = layout.column(align=True)
        col.label(text="Display:")
        col.prop(s, "xy_scale")
        if s.mode == '2D':
            col.prop(s, "height_scale")

        layout.separator()

        col = layout.column(align=True)
        col.label(text="Random:")
        col.prop(s, "seed")

        layout.separator()

        col = layout.column(align=True)
        col.label(text="Preview:")
        col.prop(s, "preview_every")
        col.prop(s, "timer_interval")

        layout.separator()

        if s.mode == '2D':
            layout.operator("rd.generate_mesh", icon="MESH_GRID")
            layout.operator("rd.generate_preview", icon="PLAY")
        else:
            layout.operator("rd.generate_mesh", icon="MESH_UVSPHERE")
            layout.operator("rd.generate_preview_3d", icon="PLAY")
