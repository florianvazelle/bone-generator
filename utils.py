import os
import bpy
import json
import random

# -------------------------------------------------------------------


def setup_selection_state(context):
    """Prepare View3D for the user can select vertices easier"""
    object_name = context.scene.active_mesh
    set_context_obj(object_name, 'MESH')
    mode_set('EDIT')
    bpy.ops.mesh.select_mode(type="VERT")
    
    # TODO : reactive xray -> lasso -> viewport shading
    # set_xray(True) 

    # for window in bpy.context.window_manager.windows:
    #     screen = window.screen
    #     for area in screen.areas:
    #         if area.type == 'VIEW_3D':
    #             for region in area.regions:
    #                 if region.type == 'WINDOW':
    #                     override = {'window': window, 'screen': screen, 'area': area, 'region': region, 'scene': bpy.context.scene,
    #                                 'edit_object': bpy.context.edit_object, 'active_object': bpy.data.objects[context.scene.active_mesh], 'selected_objects': bpy.context.selected_objects}
    #                     bpy.ops.view3d.select_lasso(override)

# -------------------------------------------------------------------


def back_to_normal_state(context):
    """Go to normal state for the View3D"""
    # set_xray(False)
    mode_set('EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    mode_set('OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

# -------------------------------------------------------------------


def mode_set(mode='OBJECT'):
    """Helper to change mode"""
    # Crash if the same mode is already set
    try:
        bpy.ops.object.mode_set(mode=mode)
    except RuntimeError:
        pass

# -------------------------------------------------------------------


def set_context_obj(object_name, object_type):
    """Helper to define active object"""
    mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
    bpy.ops.object.select_by_type(type=object_type)

# -------------------------------------------------------------------


def set_xray(state):
    """Helper to toggle xray"""
    obj = bpy.context.view_layer.objects.active

    if 'EMPTY' == obj.type or 'ARMATURE' == obj.type:
        obj.show_x_ray = state

# -------------------------------------------------------------------


def get_vertices(context, method: str = 'SELECTED', member=None) -> list:
    valid_method = ['SELECTED', 'ALL', 'MEMBER']

    if method == 'MEMBER' and member is None:
        raise 'get_vertices call with MEMBER method, need to specify a valid member'

    mode_set(mode='OBJECT')

    selected_verts = []
    obj = bpy.data.objects[context.scene.active_mesh]
    mesh = obj.data

    if method == 'MEMBER':
        matrix_world = obj.matrix_world
        points_cloud = [point.get() for point in member.points_cloud]

        for vert in mesh.vertices:
            world_co = matrix_world @ vert.co
            if (world_co[0], world_co[1], world_co[2]) in points_cloud:
                selected_verts.append(vert)
    elif method == 'SELECTED':
        for vert in mesh.vertices:
            if vert.select:
                selected_verts.append(vert)
    elif method == 'ALL':
        for vert in mesh.vertices:
            selected_verts.append(vert)
    else: 
        raise 'get_vertices call with bad method'

    return selected_verts

# -------------------------------------------------------------------


def color_to_vertices(context, vertices, color):
    mode_set(mode='OBJECT')
    mesh = bpy.data.objects[context.scene.active_mesh].data
    mode_set(mode='VERTEX_PAINT')

    r, g, b, a = color
    for polygon in mesh.polygons:
        for vert in vertices:
            for i, index in enumerate(polygon.vertices):
                if vert.index == index:
                    loop_index = polygon.loop_indices[i]
                    mesh.vertex_colors.active.data[loop_index].color = (r, g, b, a)

# -------------------------------------------------------------------


class JSONLoader:

    def __init__(self, filepath):
        self.filename = os.path.basename(filepath)
        self.path = os.path.dirname(filepath)

    def save(self, scene):
        filepath = os.path.join(self.path, self.filename)

        try:
            if os.path.isfile(filepath):
                os.remove(filepath)

            with open(filepath, 'w') as f:
                f.write(json.dumps(self.to_serializable(scene), indent=2))
        except IOError:
            print(f"Could not save setting file in {filepath}.")

    @classmethod
    def to_serializable(cls, scene):
        data = scene.selected_members
        out_data = {}

        for key, value in data.items():
            points_cloud = []

            for point in value.points_cloud.values():
                points_cloud.append(point.get())

            out_data[key] = points_cloud

        return out_data
        
    def load(self, scene):
        filepath = os.path.join(self.path, self.filename)

        try:
            raw_data = []

            with open(filepath, 'r') as f:
                raw_data = json.load(f)

            self.to_blender(raw_data, scene)
        except IOError:
            print(f"Could not open setting file in {filepath}.")

    @classmethod
    def to_blender(cls, data, scene):
        scene.selected_members.clear()

        for name, value in data.items():
            prop = scene.selected_members.add()
            prop.name = name
            prop.points_cloud.clear()
            for point in value:
                new_point = prop.points_cloud.add()
                new_point.set(point)    
