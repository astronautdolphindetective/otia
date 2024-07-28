import bpy
import bmesh
import os
import numpy as np
from math import pi, sin, cos
from mathutils import Vector
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CustomRaycastOperator(bpy.types.Operator):
    bl_idname = "object.custom_raycast_operator"
    bl_label = "Create Scan"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.perform_scan(context)
        return {'FINISHED'}

    def perform_scan(self, context):
        scene = context.scene

        scanner_base = context.scene.ray_scanner_base
        if scanner_base is None or scanner_base.type != 'EMPTY':
            self.report({'ERROR'}, "No active empty object as scanner base")
            return {'CANCELLED'}

        bpy.context.view_layer.update()

        #TODO: this is livox specific
        self.clear_points(context)

        max_distance = context.scene.ray_dist
        scans = context.scene.ray_scans
        density = context.scene.ray_density
        k = context.scene.ray_k

        logger.info("Performing scan with parameters: max_distance=%f, scans=%d, density=%d, k=%d",
                    max_distance, scans, density, k)

        hit_locations = self.generate_scan(max_distance, scans, density, k, context)

        self.create_points(hit_locations, scanner_base)

    def generate_scan(self, max_distance, scans, density, k, context):

        scene = context.scene
        depsgraph = bpy.context.evaluated_depsgraph_get()

        scanner_base = context.scene.ray_scanner_base
        world_matrix = scanner_base.matrix_world
        position = world_matrix.translation
        orientation = world_matrix.to_euler()
        orientation_degrees = (np.degrees(orientation.x), np.degrees(orientation.y), np.degrees(orientation.z))

        logger.debug("Scanner Base Position: %s", position)
        logger.debug("Scanner Base Orientation (Euler): %s radians", orientation)
        logger.debug("Scanner Base Orientation (Degrees): %s degrees", orientation_degrees)

        angle = 38.4 / 2
        radius = np.tan(np.radians(angle))
        a = radius / 2
        results = []
        current_frame = bpy.context.scene.frame_current
        start = current_frame * 2.0 * np.pi / k

        start_point = position
        logger.debug("Start point: %s", start_point)

        rotation_matrix = world_matrix.to_3x3()

        for i in range(scans):
            p = k + i
            vals = [self.logit(x) for x in np.linspace(0.01, 0.99, density)]
            vals -= np.min(vals)
            vals /= np.max(vals)

            for _ in range(density):
                lily_half = (pi / k) * 0.5 + start * (2 * pi / k)
                q = np.random.randint(0, 2 * k) * lily_half + lily_half * np.random.choice(vals, 1)[0]
                r = a * sin(start + p + q * k)
                x = r * cos(q)
                y = r * sin(q)

                direction_local = Vector((x, y, 1)).normalized()
                direction_world = rotation_matrix @ direction_local

                hit, loc, norm, idx, obj_hit, mw = scene.ray_cast(depsgraph, start_point, direction_world)

                if hit and (loc - start_point).length <= max_distance:
                    loc_relative = world_matrix.inverted() @ loc
                    results.append(Vector(loc_relative))

        logger.info("Generated %d hit locations", len(results))

        return results

    @staticmethod
    def logit(x):
        return np.log(x / (1 - x))

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

def register_base_scanner():
    bpy.utils.register_class(CustomRaycastOperator)
    

def unregister_base_scanner():
    bpy.utils.unregister_class(CustomRaycastOperator)
    del bpy.types.Scene.CustomRaycastOperator