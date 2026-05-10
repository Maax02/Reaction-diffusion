from bpy.types import PropertyGroup
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty

from .presets import (
    apply_gray_scott_2d_preset,
    apply_gray_scott_3d_preset,
    apply_brusselator_2d_preset,
    apply_brusselator_3d_preset,
    apply_fhn_2d_preset,
    apply_fhn_3d_preset,
)


class RDSettings(PropertyGroup):
    mode: EnumProperty(
        name="Mode",
        description="Reaction-diffusion mode",
        items=[
            ('2D', "2D Heightfield", "Simulate on a 2D grid and displace a plane"),
            ('3D', "3D Isosurface", "Simulate in a 3D volume and extract an isosurface mesh"),
        ],
        default='2D',
    )

    model: EnumProperty(
        name="Model",
        description="Reaction-diffusion model",
        items=[
            ('GRAY_SCOTT', "Gray-Scott", "Gray-Scott model"),
            ('BRUSSELATOR', "Brusselator", "Brusselator model"),
            ('FITZHUGH_NAGUMO', "FitzHugh-Nagumo", "Excitable reaction-diffusion model"),
        ],
        default='GRAY_SCOTT',
    )

    field_mode: EnumProperty(
        name="Field",
        description="Which field to visualize",
        items=[
            ('U', "U", "Visualize U field"),
            ('V', "V", "Visualize V field"),
        ],
        default='V',
    )

    gray_scott_2d_preset: EnumProperty(
        name="Preset",
        description="Preset parameter values",
        items=[
            ('CUSTOM', "Custom", "Use manually selected parameters"),
            ('DOTS', "Dots", "Small spot-like structures, mitosis"),
            ('WORMS', "Worms", "Labyrinth-like worm patterns"),
            ('MAZE', "Maze", "Maze-like ridges"),
            ('CORAL', "Coral", "Branching coral-like pattern"),
            ('FINGERPRINT', "Fingerprint", "Fingerprint pattern"),
            ('SYMETRIC', "Symetric", "Creates symetric patterns"),
            ('WAVES', "Waves", "Waves like oscilations"),
        ],
        default='CUSTOM',
        update=lambda self, context: apply_gray_scott_2d_preset(self),
    )
    
    gray_scott_3d_preset: EnumProperty(
        name="Preset",
        items=[
            ('CUSTOM', "Custom", "Use manually selected parameters"),
            ('TUBES', "Tubes", "Creates structure with tubes"),
            ('CUBE', "CUBE", "Creates cube, inside looks like ant nest"),
            ('SYMETRIC', "Symetric", "Creates symetric structure"),
        ],
        default='CUSTOM',
        update=lambda self, context: apply_gray_scott_3d_preset(self),
    )

    brusselator_2d_preset: EnumProperty(
        name="Preset",
        items=[
            ('CUSTOM', "Custom", "Use manually selected parameters"),
            ('WAVES', "Waves", ""),
            ('DENSE_SPIRALS', "Dense spirals", ""),
            ('SMALL_SPIRALS', "Small spirals", ""),
            ('DENSE_SPIKES', "Dense spikes", ""),
            ('SOFT_WAVES', "Soft waves", ""),
        ],
        default='CUSTOM',
        update=lambda self, context: apply_brusselator_2d_preset(self),
    )


    brusselator_3d_preset: EnumProperty(
        name="Preset",
        items=[
            ('CUSTOM', "Custom", "Use manually selected parameters"),
            ('CORAL', "Coral", "Looks like ant nest"),
            ('MINERAL', "Mineral", "Mineral-like structure"),
            ('SPIRAL', "Spiral", "Spiral patterns"),
        ],
        default='CUSTOM',
        update=lambda self, context: apply_brusselator_3d_preset(self),
    )


    fh_2d_preset: EnumProperty(
        name="Preset",
        description="Preset parameter values for FitzHugh-Nagumo",
        items=[
            ('CUSTOM', "Custom", "Use manually selected parameters"),
            ('PATTERNS', "Patterns", ""),
            ('WAVE', "Wave", "Propagating wave"),
        ],
        default='CUSTOM',
        update=lambda self, context: apply_fhn_2d_preset(self),
    )

    fh_3d_preset: EnumProperty(
        name="Preset",
        description="Preset parameter values for FitzHugh-Nagumo",
        items=[
            ('CUSTOM', "Custom", "Use manually selected parameters"),
            ('VASE', "Vase", "Creates vase-liek object"),
            ('CUBE', "Cube", ""),
            ('SPLASH', "Splash", ""),
        ],
        default='CUSTOM',
        update=lambda self, context: apply_fhn_3d_preset(self),
    )

    size: IntProperty(
        name="2D Size",
        description="2D grid size",
        default=128,
        min=8,
        soft_max=2048,
    )

    size_3d: IntProperty(
        name="3D Size",
        description="3D voxel grid size",
        default=32,
        min=8,
        soft_max=128,
    )

    steps: IntProperty(
        name="Steps",
        description="Simulation steps",
        default=4000,
        min=1,
        soft_max=20000,
    )

    Du: FloatProperty(
        name="Du",
        description="Diffusion rate of U",
        default=0.18,
        min=0.0,
        precision=5,
    )

    Dv: FloatProperty(
        name="Dv",
        description="Diffusion rate of V",
        default=0.07,
        min=0.0,
        precision=5,
    )

    F: FloatProperty(
        name="F",
        description="Gray-Scott feed rate",
        default=0.045,
        min=0.0,
        precision=5,
    )

    k: FloatProperty(
        name="k",
        description="Gray-Scott kill rate",
        default=0.060,
        min=0.0,
        precision=5,
    )

    A: FloatProperty(
        name="A",
        description="Brusselator parameter A",
        default=1.0,
        min=0.0,
        precision=5,
    )

    B: FloatProperty(
        name="B",
        description="Brusselator parameter B",
        default=3.0,
        min=0.0,
        precision=5,
    )

    dt: FloatProperty(
        name="dt",
        description="Time step",
        default=0.005,
        min=0.00001,
        soft_max=0.1,
        precision=5,
    )

    noise: FloatProperty(
        name="Noise",
        description="Random perturbation around steady state",
        default=0.03,
        min=0.0,
        soft_max=1.0,
        precision=5,
    )

    do_clamp: BoolProperty(
        name="Clamp U/V",
        description="Clamp Gray-Scott concentrations to [0, 1]. Ignored for Brusselator",
        default=True,
    )

    preview_every: IntProperty(
        name="Preview Every",
        description="Update mesh every N simulation steps",
        default=50,
        min=1,
        soft_max=1000,
    )

    timer_interval: FloatProperty(
        name="Timer (s)",
        description="Time between viewport updates",
        default=0.1,
        min=0.01,
        soft_max=2.0,
    )

    xy_scale: FloatProperty(
        name="Scale",
        description="Spacing between vertices / voxel scale",
        default=0.02,
        min=0.0001,
        soft_max=1.0,
    )

    height_scale: FloatProperty(
        name="Height Scale",
        description="Z scale for the 2D heightfield",
        default=0.5,
        min=0.0,
        soft_max=10.0,
    )

    iso_level: FloatProperty(
        name="Iso Level",
        description="Threshold for 3D isosurface extraction",
        default=0.35,
        min=0.0,
        max=1.0,
        precision=4,
    )

    perturb_2d: IntProperty(
        name="2D Perturb",
        description="Initial seeded square size in 2D",
        default=20,
        min=1,
        soft_max=256,
    )

    perturb_3d: IntProperty(
        name="3D Perturb",
        description="Initial seeded cube size in 3D",
        default=8,
        min=1,
        soft_max=64,
    )

    seed: IntProperty(
        name="Seed",
        description="Random seed",
        default=42,
        min=0,
        soft_max=1000000,
    )
    
    fh_a: FloatProperty(
        name="a",
        description="FitzHugh-Nagumo excitation parameter",
        default=0.7,
        precision=4,
    )

    fh_b: FloatProperty(
        name="b",
        description="FitzHugh-Nagumo recovery parameter",
        default=0.8,
        precision=4,
    )

    fh_eps: FloatProperty(
        name="epsilon",
        description="FitzHugh-Nagumo time scale separation",
        default=0.08,
        min=0.0001,
        precision=4,
    )

    fh_strength: FloatProperty(
        name="Trigger Strength",
        description="Initial excitation strength",
        default=1.2,
        precision=4,
    )

    fh_init_mode: EnumProperty(
        name="FHN Init",
        items=[
            ('CENTER', "Center", "Single circular excitation"),
            ('TWO_SPARKS', "Two Sparks", "Two colliding waves"),
            ('MULTI_SPARK', "Multi Spark", "Several random excitations"),
            ('BROKEN_LINE', "Broken Line", "Broken wave front, good for spirals"),
            ('HALF_PLANE', "Half Plane", "Single traveling wave front"),
        ],
        default='CENTER',
    )

    fh_num_sparks: IntProperty(
        name="Num Sparks",
        description="Number of excitation spheres in 3D FHN",
        default=8,
        min=1,
        max=64,
    )
