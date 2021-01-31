import bpy
from bpy.app.handlers import load_post, persistent

from . import operators as ops

# Handlers are callback functions "hooked" to some events of Blender's
# internal loop. They are called whenever some event occurs.
# The full list of available handlers can be found here:
# https://docs.blender.org/api/current/bpy.app.handlers.html

# -------------------------------------------------------------------

# Make sure to make this persistent otherwise handlers get reset prior
# to loading new files.


@persistent
def bone_generator_on_load(scene):
    if scene is not None:
        # Typically, you'll initialize some stuff here, or reset any
        # global state.
        # TODO : reset state bpy.ops.operator(ops.ResetSettings)
        print("A scene has been loaded!")

# -------------------------------------------------------------------


def remove_handler(handlers_list, cb):
    """Remove any handler with the same name from a given handlers list"""
    to_remove = [h for h in handlers_list if h.__name__ == cb.__name__]
    for h in to_remove:
        handlers_list.remove(h)


def register():
    unregister()  # remove handlers if they were present already
    load_post.append(bone_generator_on_load)


def unregister():
    remove_handler(load_post, bone_generator_on_load)
