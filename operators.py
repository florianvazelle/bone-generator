import os
import bpy

from bpy.types import Operator
from bpy.props import EnumProperty
from bpy.ops import view3d
from bpy_extras.io_utils import ExportHelper, ImportHelper

from .constants import MEMBERS_KEY, COLORS

from . import backend
from . import utils

# -------------------------------------------------------------------


class BaseOperator(Operator):

    @classmethod
    def poll(cls, context):
        # Ensure that the operator will not be called when the context is
        # not compatible with it. Here for instance our operator only applies
        # to a mesh.
        # It is better to do these context checks here than directly in
        # execute() because it will also for instance deactivate buttons
        # pointing to this operator in the UI.
        return context.scene.active_mesh in bpy.data.objects and bpy.data.objects[context.scene.active_mesh].type == 'MESH'

# -------------------------------------------------------------------


class ResetSettings(BaseOperator):
    bl_idname = "bone_generator.reset_settings"
    bl_label = "Reset Settings"

    def execute(self, context):
        # Reset all colors
        utils.mode_set(mode='OBJECT')
        points_cloud = utils.get_vertices(context, 'ALL')
        utils.color_to_vertices(context, points_cloud, (1, 1, 1, 1))

        context.scene.active_mesh = ""
        context.scene.selected_members.clear()
        context.scene.selection_state.reset()
        return {'FINISHED'}

# -------------------------------------------------------------------


class SaveSettings(BaseOperator, ExportHelper):
    bl_idname = "bone_generator.save_settings"
    bl_label = "Save Settings"

    filename_ext = ".json"

    def execute(self, context):
        userpath = self.properties.filepath

        if not userpath.lower().endswith('.json'):
            self.report({'WARNING'}, "You need to export a valid .json file.")

        json_loader = utils.JSONLoader(userpath)
        json_loader.save(context.scene)
        return {'FINISHED'}

# -------------------------------------------------------------------


class LoadSettings(BaseOperator, ImportHelper):
    bl_idname = "bone_generator.load_settings"
    bl_label = "Load Settings"

    def execute(self, context):
        userpath = self.properties.filepath
        if not userpath.lower().endswith('.json'):
            self.report({'WARNING'}, "You need to import a valid .json file.")

        # Reset all colors
        utils.mode_set(mode='OBJECT')
        points_cloud = utils.get_vertices(context, 'ALL')
        utils.color_to_vertices(context, points_cloud, (1, 1, 1, 1))

        # Load
        json_loader = utils.JSONLoader(userpath)
        json_loader.load(context.scene)

        # Colorize
        for member in context.scene.selected_members:
            points_cloud = utils.get_vertices(context, 'MEMBER', member=member)
            utils.color_to_vertices(context, points_cloud, COLORS[member.name])

        return {'FINISHED'}

# -------------------------------------------------------------------


class AddMember(BaseOperator):
    bl_idname = "bone_generator.add_member"
    bl_label = "Add member"

    @classmethod
    def poll(cls, context):
        found = False
        for member in context.scene.selected_members:
            if context.scene.active_member_type == member.name:
                found = True
        return super().poll(context) and not found and not context.scene.selection_state.is_active

    def execute(self, context):
        # Panel
        context.scene.selection_state.is_active = True
        context.scene.selection_state.selection_member_type = context.scene.active_member_type

        # 3D View (go to selection state)
        utils.setup_selection_state(context)
        return {'FINISHED'}

# -------------------------------------------------------------------


def reset_color_member(context, member_type) -> int:
    # Find the member in the collection `selected_members`
    for idx, member in enumerate(context.scene.selected_members):
        if member_type == member.name:
            # Get vertices in the active object mesh for the points cloud in the member
            points_cloud = utils.get_vertices(context, 'MEMBER', member=context.scene.selected_members[member_type])
            # Reset this colors
            utils.color_to_vertices(context, points_cloud, (1, 1, 1, 1))
            
            return idx
            

# -------------------------------------------------------------------


class ModifyMember(BaseOperator):
    bl_idname = "bone_generator.modify_member"
    bl_label = "modify member"

    member_type: EnumProperty(name="Member", items=MEMBERS_KEY)

    def execute(self, context):
        # Panel
        context.scene.selection_state.is_active = True
        context.scene.selection_state.selection_member_type = self.member_type

        # 3D View (go to selection state)
        utils.setup_selection_state(context)
        return {'FINISHED'}

# -------------------------------------------------------------------


class DeleteMember(BaseOperator):
    bl_idname = "bone_generator.delete_member"
    bl_label = "Delete member"

    member_type: EnumProperty(name="Member", items=MEMBERS_KEY)

    def execute(self, context):
        idx = reset_color_member(context, self.member_type)
        # Delete the member
        context.scene.selected_members.remove(idx)
        return {'FINISHED'}

# -------------------------------------------------------------------


class ValidateSelection(BaseOperator):
    bl_idname = "bone_generator.validate_selection"
    bl_label = "Validate Selection"

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.scene.selection_state.is_active

    def execute(self, context):
        reset_color_member(context, context.scene.selection_state.selection_member_type)

        # Panel
        context.scene.selection_state.is_active = False

        points_cloud = utils.get_vertices(context, 'SELECTED')
        
        utils.color_to_vertices(context, points_cloud, COLORS[context.scene.selection_state.selection_member_type])

        matrix_world = bpy.data.objects[context.scene.active_mesh].matrix_world

        found = False
        for idx, member in enumerate(context.scene.selected_members):
            if context.scene.selection_state.selection_member_type == member.name:
                found = True

                # Update
                new_member = context.scene.selected_members[idx]
                new_member.points_cloud.clear()
                for point in points_cloud:
                    new_point = new_member.points_cloud.add()
                    new_point.set(matrix_world @ point.co)

        # Add
        if not found:
            new_member = context.scene.selected_members.add()
            new_member.name = context.scene.selection_state.selection_member_type
            new_member.points_cloud.clear()
            for point in points_cloud:
                new_point = new_member.points_cloud.add()
                new_point.set(matrix_world @ point.co)

        # View 3D (back to normal state)
        utils.back_to_normal_state(context)
        return {'FINISHED'}

# -------------------------------------------------------------------


class CancelSelection(BaseOperator):
    bl_idname = "bone_generator.cancel_selection"
    bl_label = "Cancel selection"

    def execute(self, context):
        # Panel
        context.scene.selection_state.reset()

        # View 3D (back to normal state)
        utils.back_to_normal_state(context)
        return {'FINISHED'}

# -------------------------------------------------------------------


class ComputeBonesGeneration(BaseOperator):
    """Compute the centroid of the object (this message is used as description in the UI)"""
    bl_idname = "bone_generator.compute_bones_generation"
    bl_label = "Compute Bones Generation"

    @classmethod
    def poll(cls, context):
        return super().poll(context) # and len(context.scene.selected_members) == 6

    def execute(self, context):
        # The operator class defines the front-end to a function. Its core
        # logic will likely resides in a separate module (called 'backend' here)
        # as a regular python function.
        principal_components = backend.compute_bones_generation(context.active_object, utils.JSONLoader.to_serializable(context.scene))
        
        # We can report messages to the user, doc at:
        # https://docs.blender.org/api/current/bpy.types.Operator.html#bpy.types.Operator.Operator.report
        self.report({'INFO'}, f"Principal components coordinate are {principal_components}")

        if principal_components:

            # création de l'armature
            utils.mode_set(mode='OBJECT')
            bpy.ops.object.armature_add(location=(0, 0, 0))
            armature = bpy.context.active_object

            utils.mode_set(mode='EDIT')

            # On unpack les valeurs
            head, tail = principal_components['BODY']

            bone_body = bpy.context.active_bone
            # On lui assigne ses postions correspondante
            bone_body.head = head
            bone_body.tail = tail

            for key, points in principal_components.items():
                if key == 'BODY': continue

                # On unpack les valeurs
                head, tail = points

                # On crée l'armature
                bone = armature.data.edit_bones.new(name=f'Bone{key}')
                # On lui assigne ses postions correspondante
                
                if 'LEG' in key:
                    bone.head = tail
                    bone.tail = head

                    bone_racc = armature.data.edit_bones.new(name=f'Bone{key}_Raccordement')
                    bone_racc.head = bone_body.head
                    bone_racc.tail = bone.head
                
                if key == 'HEAD':
                    bone.head = tail 
                    bone.tail = head

                    bone_racc = armature.data.edit_bones.new(name=f'Bone{key}_Raccordement')
                    bone_racc.head = bone_body.tail
                    bone_racc.tail = bone.head

                if 'ARM' in key:
                    bone.head = head
                    bone.tail = tail

                    bone_racc = armature.data.edit_bones.new(name=f'Bone{key}_Raccordement')
                    bone_racc.head = bone_body.tail
                    bone_racc.tail = bone.head
                
                bone.use_relative_parent = True
                bone.parent = bone_racc

                bone_racc.use_relative_parent = True
                bone_racc.parent = bone_body

            utils.mode_set(mode='OBJECT')
            cube = bpy.data.objects[context.scene.active_mesh]
            cube.select_set(True)
            armature.select_set(True)
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')

            # debug
            # utils.mode_set('OBJECT')
            # for key, points in principal_components.items():
            #     for point in points:
            #         bpy.ops.mesh.primitive_cube_add(size=0.25, location=point)

        return {'FINISHED'}

# -------------------------------------------------------------------


classes = (
    ResetSettings,
    SaveSettings,
    LoadSettings,
    AddMember,
    ModifyMember,
    DeleteMember,
    ValidateSelection,
    CancelSelection,
    ComputeBonesGeneration
)
register, unregister = bpy.utils.register_classes_factory(classes)
