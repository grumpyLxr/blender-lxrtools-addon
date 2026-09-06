bl_info = {
    "name": "LxrTools",
    "description": "Recalculates normals outward for selected meshes, performs a BoolTool auto operation, and recalculates normals inward on the output.",
    "author": "grumpyLxr",
    "version": (1, 0, 0),
    "blender": (3, 5, 0),
    "location": "View3D > Sidebar (N-panel) > Edit",
    "category": "Object",
}

import os
import importlib

addon_folder = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
modules = (
    ".log",
    ".lxr_tools",
)


def import_modules(reload: bool):
    """
    (Re)imports all modules.
    If reload is True all modules are reloaded even if they are already imported. This is useful during development.
    """
    print("\U0001f9f0", bl_info["name"], ": Importing modules from", addon_folder)
    for mod in modules:
        module = importlib.import_module(mod, addon_folder)
        if reload:
            importlib.reload(module)


import_modules(True)

from . import log
from . import lxr_tools


def register():
    log.log("Registering Add-on")
    lxr_tools.register()


def unregister():
    log.log("Unregistering Add-on")
    lxr_tools.unregister()