import bpy
from array import array

from .deps import get_numpy, get_marching_cubes
from .math_utils import idx, normalize_field


def field_to_volume(field, size):
    np = get_numpy()
    return np.array(field, dtype=np.float32).reshape((size, size, size))


def make_base_coords(size, xy_scale=0.02):
    ox = -((size - 1) * xy_scale) * 0.5
    oy = -((size - 1) * xy_scale) * 0.5

    coords = array('f', [0.0]) * (size * size * 3)

    for y in range(size):
        for x in range(size):
            i = y * size + x
            j = i * 3
            coords[j] = ox + x * xy_scale
            coords[j + 1] = oy + y * xy_scale
            coords[j + 2] = 0.0

    return coords

def build_or_update_grid_mesh(obj_name, mesh_name, size, field, xy_scale=0.02, height_scale=0.5):
    mesh = bpy.data.meshes.get(mesh_name)
    if mesh is None:
        mesh = bpy.data.meshes.new(mesh_name)

    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        obj = bpy.data.objects.new(obj_name, mesh)
        bpy.context.collection.objects.link(obj)
    else:
        obj.data = mesh

    ox = -((size - 1) * xy_scale) * 0.5
    oy = -((size - 1) * xy_scale) * 0.5

    verts = []
    for y in range(size):
        for x in range(size):
            z = field[idx(x, y, size)] * height_scale
            verts.append((ox + x * xy_scale, oy + y * xy_scale, z))

    faces = []
    for y in range(size - 1):
        row = y * size
        next_row = (y + 1) * size
        for x in range(size - 1):
            a = row + x
            b = row + x + 1
            c = next_row + x + 1
            d = next_row + x
            faces.append((a, b, c, d))

    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    for p in mesh.polygons:
        p.use_smooth = True

    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    return obj

def update_grid_mesh_heights(obj, size, field, height_scale=0.5, base_coords=None):
    mesh = obj.data
    n = size * size

    if len(mesh.vertices) != n:
        raise ValueError("Mesh vertex count does not match size*size")

    if base_coords is None or len(base_coords) != n * 3:
        raise ValueError("base_coords must have length size*size*3")

    coords = array('f', base_coords)

    for i in range(n):
        coords[i * 3 + 2] = field[i] * height_scale

    mesh.vertices.foreach_set("co", coords)
    mesh.update()

def build_isosurface_mesh(obj_name, mesh_name, verts, faces, voxel_scale=0.02, grid_size=32):
    mesh = bpy.data.meshes.get(mesh_name)
    if mesh is None:
        mesh = bpy.data.meshes.new(mesh_name)

    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        obj = bpy.data.objects.new(obj_name, mesh)
        bpy.context.collection.objects.link(obj)
    else:
        obj.data = mesh

    offset = ((grid_size - 1) * voxel_scale) * 0.5
    scaled_verts = [
        (
            (x * voxel_scale) - offset,
            (y * voxel_scale) - offset,
            (z * voxel_scale) - offset,
        )
        for z, y, x in verts
    ]

    if hasattr(faces, "tolist"):
        faces = faces.tolist()

    mesh.clear_geometry()
    mesh.from_pydata(scaled_verts, [], faces)
    mesh.update()

    for p in mesh.polygons:
        p.use_smooth = True

    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    return obj

def update_3d_preview_mesh(u, v, s):
    size = s.size_3d
    field = u if s.field_mode == 'U' else v

    if s.model in {'BRUSSELATOR', 'FITZHUGH_NAGUMO'}:
        field = normalize_field(field)

    volume = field_to_volume(field, size)

    fmin = float(volume.min())
    fmax = float(volume.max())

    if not (fmin <= s.iso_level <= fmax):
        print(f"Iso level {s.iso_level:.4f} outside range [{fmin:.4f}, {fmax:.4f}]")
        return None

    marching_cubes = get_marching_cubes()
    verts, faces, normals, values = marching_cubes(volume, level=s.iso_level)

    obj = build_isosurface_mesh(
        "RD_Object_3D",
        "RD_Object_3D_Mesh",
        verts,
        faces,
        voxel_scale=s.xy_scale,
        grid_size=size,
    )

    return obj
