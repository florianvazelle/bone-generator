from . import handlers
from . import panels
from . import operators
from . import properties
import bpy
bl_info = {
    "name": "Bone Generator",
    "author": "Florian Vazelle",
    "version": (0, 1, 0),
    "blender": (2, 91, 0),
    "location": "Properties > Scene",
    "description": "Bones generation for a 3D mesh with the principal component analysis method",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/florianvazelle/bone-generator/issues",
    "support": "TESTING",
    "category": "Rigging",
}

# -------------------------------------------------------------------
# This section is dedicated to make the "Reload Scripts" operator of
# Blender truly work to be able to update the add-on while developping.
# This feature only reloads this __init__ file, so we force reloading all
# other files here.

# When loaded is already in local, we know this is called by "Reload plugins"
if locals().get('loaded') or True:
    loaded = False
    from importlib import reload
    from sys import modules
    import os

    for i in range(3):  # Try up to three times, in case of ordering errors
        err = False
        modules[__name__] = reload(modules[__name__])
        submodules = list(modules.items())
        for name, module in submodules:
            if name.startswith(f"{__package__}."):
                if module.__file__ is None:
                    # This is a namespace, no need to do anything
                    continue
                elif not os.path.isfile(module.__file__):
                    # File has been removed
                    del modules[name]
                    del globals()[name]
                else:
                    print(f"Reloading: {module}")
                    try:
                        globals()[name] = reload(module)
                    except Exception as e:
                        print(e)
                        err = True
        if not err:
            break
        #del reload, modules

# -------------------------------------------------------------------


def register():
    properties.register()
    operators.register()
    panels.register()
    handlers.register()


def unregister():
    properties.unregister()
    operators.unregister()
    panels.unregister()
    handlers.unregister()
