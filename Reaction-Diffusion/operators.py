import bpy

from .math_utils import normalize_field
from .simulations import *
from .mesh_utils import (
    build_or_update_grid_mesh,
    update_grid_mesh_heights,
    make_base_coords,
    field_to_volume,
    build_isosurface_mesh,
    update_3d_preview_mesh,
)
from .deps import get_marching_cubes


class RD_OT_generate(bpy.types.Operator):
    bl_idname = "rd.generate_mesh"
    bl_label = "Generate RD Mesh"
    bl_description = "Generate reaction-diffusion mesh"

    def execute(self, context):
        s = context.scene.rd_settings

        if s.mode == '2D':
            size = s.size

            if s.model == 'GRAY_SCOTT':
                u, v = simulate_gray_scott_fast(
                    size, s.steps, s.Du, s.Dv, s.F, s.k,
                    seed=s.seed,
                    perturb=s.perturb_2d,
                    do_clamp=s.do_clamp,
                )

            elif s.model == 'BRUSSELATOR':
                u, v = simulate_brusselator_fast(
                    size, s.steps, s.Du, s.Dv, s.A, s.B,
                    dt=s.dt,
                    seed=s.seed,
                    noise=s.noise,
                    perturb=s.perturb_2d,
                )

            else:
                u, v = simulate_fitzhugh_nagumo_fast(
                    size, s.steps, s.Du, s.Dv,
                    s.fh_a, s.fh_b, s.fh_eps,
                    dt=s.dt,
                    seed=s.seed,
                    noise=s.noise,
                    perturb=s.perturb_2d,
                    strength=s.fh_strength,
                    mode=s.fh_init_mode,
                )

            field = u if s.field_mode == 'U' else v
            
            # brusselator is too spiky
            if s.model in {'BRUSSELATOR', 'FITZHUGH_NAGUMO'}:
                field = normalize_field(field)

            build_or_update_grid_mesh(
                "RD_Object",
                "RD_Object_Mesh",
                size,
                field,
                s.xy_scale,
                s.height_scale,
            )

            self.report({'INFO'}, f"2D {s.model} mesh generated")
            return {'FINISHED'}

        # 3D mode
        if s.model not in {'GRAY_SCOTT', 'BRUSSELATOR', 'FITZHUGH_NAGUMO'}:
            self.report({'ERROR'}, "3D mode is currently implemented only for Gray-Scott and Brusselator and FHN")
            return {'CANCELLED'}


        size = s.size_3d

        if s.model == 'GRAY_SCOTT':
            u, v = simulate_gray_scott_3d_fast(
                size,
                s.steps,
                s.Du,
                s.Dv,
                s.F,
                s.k,
                seed=s.seed,
                perturb=s.perturb_3d,
                do_clamp=s.do_clamp,
            )

        elif s.model == 'BRUSSELATOR':
            u, v = simulate_brusselator_3d_fast(
                size,
                s.steps,
                s.Du,
                s.Dv,
                s.A,
                s.B,
                dt=s.dt,
                seed=s.seed,
                noise=s.noise,
            )
            
        elif s.model == 'FITZHUGH_NAGUMO':
            u, v = simulate_fitzhugh_nagumo_3d_fast(
                size,
                s.steps,
                s.Du,
                s.Dv,
                s.fh_a,
                s.fh_b,
                s.fh_eps,
                dt=s.dt,
                seed=s.seed,
                noise=s.noise,
                perturb=s.perturb_3d,
                strength=s.fh_strength,
                num_sparks=getattr(s, 'fh_num_sparks', 8),
            )

        field = u if s.field_mode == 'U' else v
        
        if s.model in {'BRUSSELATOR', 'FITZHUGH_NAGUMO'}:
            field = normalize_field(field)

        volume = field_to_volume(field, size)

        try:
            marching_cubes = get_marching_cubes()
            verts, faces, normals, values = marching_cubes(volume, level=s.iso_level)
        except Exception as e:
            self.report({'ERROR'}, f"Marching cubes failed: {e}")
            return {'CANCELLED'}

        build_isosurface_mesh(
            "RD_Object_3D",
            "RD_Object_3D_Mesh",
            verts,
            faces,
            voxel_scale=s.xy_scale,
            grid_size=size,
        )

        self.report({'INFO'}, f"3D {s.model} isosurface generated")
        return {'FINISHED'}

class RD_OT_generate_preview(bpy.types.Operator):
    bl_idname = "rd.generate_preview"
    bl_label = "Preview RD Mesh"
    bl_description = "Generate reaction-diffusion mesh progressively"

    _timer = None
    _u = None
    _v = None
    _obj = None
    _current_step = 0
    _base_coords = None

    def modal(self, context, event):
        if event.type == 'ESC':
            self.cancel(context)
            self.report({'INFO'}, "RD preview cancelled")
            return {'CANCELLED'}

        if event.type == 'TIMER':
            s = context.scene.rd_settings

            if s.mode != '2D':
                self.cancel(context)
                self.report({'WARNING'}, "Preview is currently only implemented for 2D mode")
                return {'CANCELLED'}

            if self._current_step >= s.steps:
                self.cancel(context)
                self.report({'INFO'}, "RD preview finished")
                return {'FINISHED'}

            steps_now = min(s.preview_every, s.steps - self._current_step)

            evolve_model_2d_inplace(self._u, self._v, s, steps_now)
            self._current_step += steps_now

            field = self._u if s.field_mode == 'U' else self._v
            
            # brusselator is too spiky
            if s.model in {'BRUSSELATOR', 'FITZHUGH_NAGUMO'}:
                field = normalize_field(field)

            update_grid_mesh_heights(
                self._obj,
                s.size,
                field,
                s.height_scale,
                self._base_coords,
            )

            if context.area:
                context.area.tag_redraw()

        return {'PASS_THROUGH'}

    def execute(self, context):
        s = context.scene.rd_settings

        if s.mode != '2D':
            self.report({'WARNING'}, "Preview is currently only available for 2D mode")
            return {'CANCELLED'}

        self._u, self._v = init_model_state_2d(s)
        self._current_step = 0
        self._base_coords = make_base_coords(s.size, s.xy_scale)

        field = self._u if s.field_mode == 'U' else self._v
        if s.model in {'BRUSSELATOR', 'FITZHUGH_NAGUMO'}:
            field = normalize_field(field)

        self._obj = build_or_update_grid_mesh(
            "RD_Object",
            "RD_Object_Mesh",
            s.size,
            field,
            s.xy_scale,
            s.height_scale,
        )

        wm = context.window_manager
        self._timer = wm.event_timer_add(s.timer_interval, window=context.window)
        wm.modal_handler_add(self)

        self.report({'INFO'}, f"2D {s.model} preview started (ESC to cancel)")

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        if self._timer is not None:
            wm.event_timer_remove(self._timer)
            self._timer = None

class RD_OT_generate_preview_3d(bpy.types.Operator):
    bl_idname = "rd.generate_preview_3d"
    bl_label = "Preview 3D RD Mesh"
    bl_description = "Generate 3D reaction-diffusion mesh progressively"

    _timer = None
    _u = None
    _v = None
    _current_step = 0
    _obj = None

    def modal(self, context, event):
        if event.type == 'ESC':
            self.cancel(context)
            self.report({'INFO'}, "3D RD preview cancelled")
            return {'CANCELLED'}

        if event.type == 'TIMER':
            s = context.scene.rd_settings

            if s.mode != '3D':
                self.cancel(context)
                self.report({'WARNING'}, "3D preview requires 3D mode")
                return {'CANCELLED'}

            if self._current_step >= s.steps:
                self.cancel(context)
                self.report({'INFO'}, "3D RD preview finished")
                return {'FINISHED'}

            steps_now = min(s.preview_every, s.steps - self._current_step)

            evolve_model_3d_inplace(self._u, self._v, s, steps_now)
            self._current_step += steps_now

            try:
                self._obj = update_3d_preview_mesh(self._u, self._v, s)
            except Exception as e:
                print("3D preview mesh update failed:", e)

            if context.area:
                context.area.tag_redraw()

        return {'PASS_THROUGH'}

    def execute(self, context):
        s = context.scene.rd_settings

        if s.mode != '3D':
            self.report({'WARNING'}, "3D preview is only available in 3D mode")
            return {'CANCELLED'}

        if s.model not in {'GRAY_SCOTT', 'BRUSSELATOR', 'FITZHUGH_NAGUMO'}:
            self.report({'ERROR'}, "Unsupported model for 3D preview")
            return {'CANCELLED'}

        self._u, self._v = init_model_state_3d(s)
        self._current_step = 0

        try:
            self._obj = update_3d_preview_mesh(self._u, self._v, s)
        except Exception as e:
            print("Initial 3D mesh update failed:", e)

        wm = context.window_manager
        self._timer = wm.event_timer_add(s.timer_interval, window=context.window)
        wm.modal_handler_add(self)

        self.report({'INFO'}, f"3D {s.model} preview started (ESC to cancel)")
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        if self._timer is not None:
            wm.event_timer_remove(self._timer)
            self._timer = None
