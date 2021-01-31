import bpy

from bpy.types import Scene, PropertyGroup
from bpy.props import (
    PointerProperty, BoolProperty, EnumProperty,
    StringProperty, CollectionProperty, FloatProperty
)

from .constants import MEMBERS_KEY

# -------------------------------------------------------------------
# A property group can have custom methods attached to it for a more
# convenient access. Members 'sample_count', 'accumulated' and 'accumulated_sq'
# are what is stored in .blend files but average() is used for display in panels
# and add_sample() in operators. A property group can hence contain logic.

# TODO : use the default bpy.props.FloatVectorProperty


class FloatVectorProperty(PropertyGroup):
    x: FloatProperty()
    y: FloatProperty()
    z: FloatProperty()

    def get(self) -> tuple:
        return (self.x, self.y, self.z)

    def set(self, value: tuple):
        self.x = value[0]
        self.y = value[1]
        self.z = value[2]


class MemberProperty(PropertyGroup):

    # member_type: EnumProperty(name="Member", items=MEMBERS_KEY) # Instantiated by default
    points_cloud: CollectionProperty(type=FloatVectorProperty)

# -------------------------------------------------------------------


class SelectionStateProperty(PropertyGroup):

    is_active: BoolProperty(name="Is User Selection State", default=False)
    selection_member_type: EnumProperty(name="Selection Member", items=MEMBERS_KEY)

    def reset(self):
        self.is_active = False

# -------------------------------------------------------------------


classes = (
    FloatVectorProperty, MemberProperty, SelectionStateProperty,
)
register_cls, unregister_cls = bpy.utils.register_classes_factory(classes)


def register():
    register_cls()

    # Add properties to all scenes
    Scene.active_member_type = EnumProperty(name="Member", items=MEMBERS_KEY)
    Scene.active_mesh = StringProperty(name="Target")  # Normally is a Human model
    Scene.selected_members = CollectionProperty(name="Members", type=MemberProperty)
    Scene.selection_state = PointerProperty(type=SelectionStateProperty)


def unregister():
    unregister_cls()

    del Scene.active_member_type
    del Scene.active_mesh
    del Scene.selected_members
    del Scene.selection_state
