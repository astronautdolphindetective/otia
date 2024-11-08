import bpy
import os
import json
import bmesh
import logging
import numpy as np
from mathutils import Vector
from pathlib import Path
import sys


#begin preprocessing
project_root = "/home/jan/Workspace/lidar_scanner2/otia"
#end preprocessing 
sys.path.append(project_root)


print("sys.path after:", sys.path)

from sensor.models.lidar.lidar_functionality import *
from sensor.models.lidar.ros_info import save_lidar_ros_info

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

functions = {
    "livox_mid40": livox_mid_40,
    "demo": demo,
    "velodyne_hdl64": velodyne_hdl64
}

def get_lidar_parameters():
    filepath = os.path.join(project_root, "sensor", "models", "lidar", "models.json")
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        logger.info("%s", e)
        print(f"An error occurred: {e}")
        return None

lidar_data = get_lidar_parameters()




def save_hit_locations_as_numpy(hit_locations, folder_path, file_name="hit_locations.npy"):
    try:
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        hit_locations_array = np.array([loc.to_tuple() for loc in hit_locations])

        file_path = os.path.join(folder_path, file_name)

        np.save(file_path, hit_locations_array)
    except Exception as e:
        logger.error(f"Failed to save hit locations: {e}")


def create_custom_raycast_operator(scanner_name, parameters, selected_lidar):

    outpath = bpy.context.scene.folder_path
    logger.info("outpath %s", outpath)
    scanner_folder = os.path.join(outpath, "lidar", scanner_name)
    save_lidar_ros_info(scanner_folder)

    class CustomRaycastOperator(bpy.types.Operator):
        bl_idname = f"object.custom_raycast_{scanner_name}"
        bl_label = f"Custom Raycast {scanner_name}"
        bl_options = {'REGISTER', 'UNDO'}
        hz = bpy.context.scene.lidar_hz

        def execute(self, context):
            return self.perform_scan(context)


        def perform_scan(self, context):
            scene = context.scene
            outpath = None
            
            current_frame = bpy.context.scene.frame_current
            
            if scene.simulation_running and scene.milliseconds_per_frame * current_frame % self.hz != 0:
                return {"FINISHED"}

            try:
                outpath = context.scene.folder_path
            except Exception as e:
                logger.info("%s", e)

            depsgraph = bpy.context.evaluated_depsgraph_get()

            scanner_base = scene.objects.get(scanner_name)
            world_matrix = scanner_base.matrix_world
            position = world_matrix.translation

            if scanner_base is None or scanner_base.type != 'EMPTY':
                self.report({'ERROR'}, "No active empty object as scanner base")
                return {'CANCELLED'}

            bpy.context.view_layer.update()

            max_distance = parameters['max_distance']
            res = functions[selected_lidar](current_frame, parameters)

            rotation_matrix = world_matrix.to_3x3()
            hit_data = []

            for e in res:
                direction_local = Vector(e).normalized()
                direction_world = rotation_matrix @ direction_local

                hit, loc, norm, idx, obj_hit, mw = scene.ray_cast(depsgraph, position, direction_world)

                if hit and (loc - position).length <= max_distance:
                    loc_relative = world_matrix.inverted() @ loc
                    intensity = 1.0  # Default intensity value


                    if obj_hit and obj_hit.active_material:
                        mat = obj_hit.active_material
                        if mat.use_nodes:
                            # Look for the Principled BSDF node
                            principled_node = next((node for node in mat.node_tree.nodes if node.type == 'BSDF_PRINCIPLED'), None)
                            if principled_node:
                                # Get the base color from the Principled BSDF node's input
                                base_color_socket = principled_node.inputs.get('Base Color')
                                if base_color_socket:
                                    color = base_color_socket.default_value
                                    intensity = sum(color[:3]) / 3.0  # Average RGB value
                        else:
                            color = mat.diffuse_color
                            intensity = sum(color[:3]) / 3.0  # Average RGB value
                    #logger.info("intensity %s", intensity)
                    logger.info("obj name: %s",obj_hit.name)
                    intensity *= 255
                    hit_data.append((*loc_relative, intensity))

            # Create a folder for the scanner if it doesn't exist
            scanner_folder = os.path.join(outpath, "lidar", scanner_name)
            Path(scanner_folder).mkdir(parents=True, exist_ok=True)

            # Convert the list to a NumPy array
            hit_data_array = np.array(hit_data)

            # Save the hit data array including intensities
            file_path = os.path.join(scanner_folder, f"{current_frame}.npy")
            np.save(file_path, hit_data_array)

            # Update the points in the scene (optional visualization)
            self.create_points(hit_data_array[:, :3], scanner_base)

            return {'FINISHED'}
 

        def create_points(self, locations, scanner_base):
            # Ensure the "Scans" collection exists
            scans_collection = bpy.data.collections.get("Scans")
            if not scans_collection:
                scans_collection = bpy.data.collections.new("Scans")
                bpy.context.scene.collection.children.link(scans_collection)

            # Delete old points with the same name
            for obj in list(scans_collection.objects):
                if obj.name.startswith(f"{scanner_name}"):
                    bpy.data.objects.remove(obj, do_unlink=True)

            # Create a new mesh for the point cloud
            mesh = bpy.data.meshes.new(name=f"{scanner_name}")
            obj = bpy.data.objects.new(f"{scanner_name}", mesh)
            scans_collection.objects.link(obj)

            # Create the point cloud geometry using BMesh
            bm = bmesh.new()
            
            # Convert numpy arrays to Blender Vectors for transformation
            for loc in locations:
                # Convert the numpy array to a Blender Vector
                loc_vector = Vector(loc[:3])
                # Apply the matrix transformation
                loc_absolute = scanner_base.matrix_world @ loc_vector
                # Add the transformed location as a vertex
                bm.verts.new(loc_absolute)
            
            bm.to_mesh(mesh)
            bm.free()

            # Update the view layer to reflect changes
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)



    # Register the operator class
    bpy.utils.register_class(CustomRaycastOperator)
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
            sensor_name = scene.lidar_name

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
