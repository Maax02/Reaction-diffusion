import bpy
import os
import sys
import subprocess
import importlib

ADDON_DIR = os.path.dirname(__file__)
DEPS_DIR = os.path.join(ADDON_DIR, "dependencies")
CYTHON_DIR = os.path.join(ADDON_DIR, "cython")


def refresh_dependency_paths():
    if os.path.exists(DEPS_DIR) and DEPS_DIR not in sys.path:
        sys.path.insert(0, DEPS_DIR)
    if os.path.exists(CYTHON_DIR) and CYTHON_DIR not in sys.path:
        sys.path.insert(0, CYTHON_DIR)
    importlib.invalidate_caches()


refresh_dependency_paths()


def is_numpy_installed():
    try:
        import numpy  # noqa: F401
        return True
    except ImportError:
        return False


def is_skimage_installed():
    try:
        from skimage.measure import marching_cubes  # noqa: F401
        return True
    except ImportError:
        return False


def are_dependencies_installed():
    return is_numpy_installed() and is_skimage_installed()


def install_python_dependencies():
    os.makedirs(DEPS_DIR, exist_ok=True)
    environ_copy = dict(os.environ)
    environ_copy["PYTHONNOUSERSITE"] = "1"
    python_exe = sys.executable

    try:
        import ensurepip
        ensurepip.bootstrap()
    except Exception:
        pass

    subprocess.check_call([
        python_exe,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "--target",
        DEPS_DIR,
        "numpy",
        "scikit-image",
    ], env=environ_copy)

    refresh_dependency_paths()


class RD_OT_install_dependencies(bpy.types.Operator):
    bl_idname = "rd.install_dependencies"
    bl_label = "Install RD Dependencies"
    bl_description = "Install NumPy and scikit-image into the addon dependencies folder"

    def execute(self, context):
        self.report({'INFO'}, "Installing dependencies. Blender may freeze. See console.")
        try:
            install_python_dependencies()
        except Exception as e:
            self.report({'ERROR'}, f"Dependency installation failed: {e}")
            return {'CANCELLED'}

        if are_dependencies_installed():
            self.report({'INFO'}, "Dependencies installed successfully.")
        else:
            self.report({'WARNING'}, "Dependencies installed, but Blender may need restart.")
        return {'FINISHED'}


def get_numpy():
    try:
        import numpy as np
        return np
    except ImportError as e:
        raise ImportError("NumPy not found. Use the 'Install RD Dependencies' button first.") from e


def get_marching_cubes():
    try:
        from skimage.measure import marching_cubes
        return marching_cubes
    except ImportError as e:
        raise ImportError("scikit-image not found. Use the 'Install RD Dependencies' button first.") from e


try:
    from .cython import rd_core
except ImportError:
    try:
        import rd_core
    except ImportError as e:
        raise ImportError(
            "Compiled Cython module rd_core was not found. Include the compiled .pyd file in the cython folder."
        ) from e
