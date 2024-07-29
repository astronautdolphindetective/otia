import bpy
import os
import json
import bmesh
import logging
import numpy as np
from math import pi, sin, cos
from mathutils import Vector
from pathlib import Path
import sys

path = Path(bpy.data.filepath).parent
project_root = path / "otia"

if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

print("sys.path after:", sys.path)

#from sensor.models.lidar.scanner_base import register_base_scanner, unregister_base_scanner
from sensor.models.lidar.lidar_functionality import *

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

functions = {
    "livox_mid40": livox_mid_40
}

def get_lidar_parameters():
    filepath = os.path.join(project_root, "sensor","models", "lidar", "models.json")
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        logger.info("%s", e)
        print(f"An error occurred: {e}")
        return None

lidar_data = get_lidar_parameters()

def create_custom_raycast_operator(scanner_name, parameters, selected_lidar):

    class CustomRaycastOperator(bpy.types.Operator):
        bl_idname = f"object.custom_raycast_{scanner_name}"
        bl_label = f"Custom Raycast {scanner_name}"
        bl_options = {'REGISTER', 'UNDO'}

        def execute(self, context):
            return self.perform_scan(context)

        def perform_scan(self, context):
            logger.info("Scanning the scene")
            scene = context.scene
            depsgraph = bpy.context.evaluated_depsgraph_get()

            scanner_base = scene.objects.get(scanner_name)
            world_matrix = scanner_base.matrix_world
            position = world_matrix.translation
 
            
            if scanner_base is None or scanner_base.type != 'EMPTY':
                self.report({'ERROR'}, "No active empty object as scanner base")
                return {'CANCELLED'}

            bpy.context.view_layer.update()

            max_distance = parameters['max_distance']
            current_frame = bpy.context.scene.frame_current
            res = functions[selected_lidar](current_frame, parameters)

            rotation_matrix = world_matrix.to_3x3()
            hit_locations = []

            for e in res:
                direction_local = Vector(e).normalized()
                direction_world = rotation_matrix @ direction_local

                hit, loc, norm, idx, obj_hit, mw = scene.ray_cast(depsgraph, position, direction_world)

                if hit and (loc - position).length <= max_distance:
                    loc_relative = world_matrix.inverted() @ loc
                    hit_locations.append(Vector(loc_relative))

            logger.info("Generated %d hit locations", len(hit_locations))
            self.create_points(hit_locations, scanner_base)

        def create_points(self, locations, scanner_base):
            mesh = bpy.data.meshes.new(name="RaycastPoints")
            obj = bpy.data.objects.new("RaycastPoints", mesh)

            scene = bpy.context.scene
            scene.collection.objects.link(obj)

            bm = bmesh.new()
            for loc in locations:
                loc_absolute = scanner_base.matrix_world @ loc
                bm.verts.new(loc_absolute)
            bm.to_mesh(mesh)
            bm.free()

            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

            logger.info("Created point cloud with %d points", len(locations))

        def clear_points(self, context):
            scene = context.scene
            for obj in list(scene.objects):
                if obj.name.startswith("RaycastPoints"):
                    bpy.data.objects.remove(obj, do_unlink=True)
            logger.info("Cleared previous point cloud objects")

    # Register the operator class
    bpy.utils.register_class(CustomRaycastOperator)
    logger.info("New custom raycast operator was created")
    return CustomRaycastOperator


class CreateScannerOperator(bpy.types.Operator):
    bl_idname = "object.create_scanner"
    bl_label = "Create Scanner"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        selected_lidar = scene.lidar_selection_dropdown
        if selected_lidar:
            parameters = lidar_data[selected_lidar]["parameters"]
            params = {param_name: getattr(scene, f"lidar_{param_name}") for param_name in parameters.keys()}
            sensor_name = scene.sensor_name

            # Create the scanner base
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.empty_add(type='ARROWS', location=(0, 0, 0))
            scanner_base = context.active_object
            scanner_base.name = sensor_name if sensor_name else "New Scanner"

            # Create a custom collection if it doesn't exist
            if "LiDAR" not in bpy.data.collections:
                sensors_collection = bpy.data.collections.new("LiDAR")
                bpy.context.scene.collection.children.link(sensors_collection)
            else:
                sensors_collection = bpy.data.collections.get("LiDAR")

            # Add the scanner to the collection
            sensors_collection.objects.link(scanner_base)
            context.collection.objects.unlink(scanner_base)

            # Create a custom raycast operator for the new scanner
            create_custom_raycast_operator(sensor_name, params, selected_lidar)

            # Update the UI
            context.area.tag_redraw()
            context.view_layer.update()

        return {'FINISHED'}

def register_create_scanner():
    bpy.utils.register_class(CreateScannerOperator)

def unregister_create_scanner():
    bpy.utils.unregister_class(CreateScannerOperator)
