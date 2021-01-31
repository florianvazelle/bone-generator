import bpy
from bpy.types import Panel

from . import operators as ops

from .constants import MEMBERS_KEY, COLORS

# -------------------------------------------------------------------


class BoneGeneratorPanel(Panel):
    bl_label = "Bone Generator"
    bl_idname = "SCENE_PT_BoneGeneratorPanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        # The draw() method is called by Blender's UI system when
        # drawing the panel. It must use self.layout to add items.
        # The draw() function can be long, so feel free to
        # break it up in several methods.
        scene = context.scene
        layout = self.layout

        self.draw_settings(scene, layout)

    def draw_settings(self, scene, layout):
        """Show settings (select object, add member ...)"""

        # Use operator's bl_idname rather than explicitely writing
        layout.operator(ops.ComputeBonesGeneration.bl_idname)

        # TODO : poll ...
        layout.operator(ops.SaveSettings.bl_idname)
        layout.operator(ops.LoadSettings.bl_idname)

        # Reset all parameters
        layout.operator(ops.ResetSettings.bl_idname)

        # Select object to edit, in the scene
        layout.prop_search(scene, "active_mesh", scene,
                           "objects", icon='OBJECT_DATA', text="Object")

        # Add a new member
        row = layout.row()
        # Select, with active_member_type like option
        row.prop(scene, "active_member_type")
        row.operator(ops.AddMember.bl_idname, text="", icon="ADD")

        # Scene value
        selected_members = scene.selected_members
        selection_state = scene.selection_state

        valid_members_keys = [x[0] for x in MEMBERS_KEY]

        # Draw selection interaction
        if selection_state.is_active:
            row = layout.row()
            row.label(text=selection_state.selection_member_type, icon="SCREEN_BACK")
            row.operator(ops.ValidateSelection.bl_idname, text="", icon="CHECKMARK")
            row.operator(ops.CancelSelection.bl_idname, text="", icon="CANCEL")
            del valid_members_keys[valid_members_keys.index(selection_state.selection_member_type)]

        # Draw selected member
        for member in selected_members:
            member_name = member.name
            if member_name in valid_members_keys:  # check if this is a valid key
                # TODO : icon to visualize point_cloud (color)
                row = layout.row()
                row.template_node_socket(color=COLORS[member_name])
                row.label(text=member_name)

                props = row.operator(ops.ModifyMember.bl_idname, text="", icon="MODIFIER")
                props.member_type = member_name

                props = row.operator(ops.DeleteMember.bl_idname, text="", icon="TRASH")
                props.member_type = member_name

# -------------------------------------------------------------------


classes = (
    BoneGeneratorPanel,
)
register, unregister = bpy.utils.register_classes_factory(classes)
