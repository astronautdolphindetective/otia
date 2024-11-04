import bpy
import logging
from bpy.props import FloatProperty, FloatVectorProperty, EnumProperty, StringProperty, PointerProperty
import os
import json
from pathlib import Path
import sys


project_root = '/home/jan/Workspace/lidar_scanner/otia'
sys.path.append(project_root)


from sensor.models.cam.ros_info import save_cam_ros_info
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



class CameraSettings(bpy.types.PropertyGroup):
    name: StringProperty(
        name="Camera Name",
        description="Name of the camera",
        default="Camera"
    )
    lens: FloatProperty(
        name="Focal Length",
        description="Focal length in millimeters",
        default=50.0,
        min=1.0,
        max=500.0
    )
    sensor_width: FloatProperty(
        name="Sensor Width",
        description="Sensor width in millimeters",
        default=36.0,
        min=1.0,
        max=100.0
    )
    location: FloatVectorProperty(
        name="Location",
        description="Location of the camera",
        default=(0.0, -3.0, 2.0)
    )
    rotation: FloatVectorProperty(
        name="Rotation",
        description="Rotation of the camera",
        default=(1.1, 0.0, 0.8),
        subtype='EULER'
    )
    camera_type: EnumProperty(
        name="Camera Type",
        description="Type of the camera",
        items=[
            ('PERSP', "Perspective", "Perspective Camera"),
            ('ORTHO', "Orthographic", "Orthographic Camera")
        ],
        default='PERSP'
    )
    clip_start: FloatProperty(
        name="Clip Start",
        description="Near clipping distance",
        default=0.1,
        min=0.01,
        max=1000.0
    )
    clip_end: FloatProperty(
        name="Clip End",
        description="Far clipping distance",
        default=1000.0,
        min=1.0,
        max=10000.0
    )
    shift_x: FloatProperty(
        name="Shift X",
        description="Horizontal shift",
        default=0.0,
        min=-2.0,
        max=2.0
    )
    shift_y: FloatProperty(
        name="Shift Y",
        description="Vertical shift",
        default=0.0,
        min=-2.0,
        max=2.0
    )
    sensor_fit: EnumProperty(
        name="Sensor Fit",
        description="Method to fit image and sensor",
        items=[
            ('AUTO', "Auto", "Fit to the dimensions of the render"),
            ('HORIZONTAL', "Horizontal", "Fit to the width of the sensor"),
            ('VERTICAL', "Vertical", "Fit to the height of the sensor")
        ],
        default='AUTO'
    )




class CAMERA_OT_create_update(bpy.types.Operator):
    bl_label = "Create/Update Camera"
    bl_idname = "camera.create_update"
    
    def execute(self, context):
        scene = context.scene
        camera_settings = scene.camera_settings

        # Check if the "Cameras" collection exists, if not, create it
        if "Cameras" not in bpy.data.collections:
            camera_collection = bpy.data.collections.new("Cameras")
            scene.collection.children.link(camera_collection)
        else:
            camera_collection = bpy.data.collections["Cameras"]

        # Create or update the camera object
        if camera_settings.name not in bpy.data.objects:
            # Create a new camera object
            camera_data = bpy.data.cameras.new(name=camera_settings.name)
            camera_object = bpy.data.objects.new(name=camera_settings.name, object_data=camera_data)
            camera_collection.objects.link(camera_object)

            # Save ROS data
            outpath = bpy.context.scene.folder_path
            logger.info("outpath %s", outpath)
            scanner_folder = os.path.join(outpath, "cam", camera_settings.name)
            save_cam_ros_info(scanner_folder)

        else:
            # Update the existing camera object
            camera_object = bpy.data.objects[camera_settings.name]
            camera_data = camera_object.data

        # Set the camera's data properties
        camera_data.lens = camera_settings.lens
        camera_data.sensor_width = camera_settings.sensor_width
        camera_data.type = camera_settings.camera_type
        camera_data.clip_start = camera_settings.clip_start
        camera_data.clip_end = camera_settings.clip_end
        camera_data.shift_x = camera_settings.shift_x
        camera_data.shift_y = camera_settings.shift_y
        camera_data.sensor_fit = camera_settings.sensor_fit

        # Position the camera in the scene
        camera_object.location = camera_settings.location
        camera_object.rotation_euler = camera_settings.rotation

        # Make the new camera the active camera
        scene.camera = camera_object

        return {'FINISHED'}

def regist_camera_creator():
    bpy.utils.register_class(CAMERA_OT_create_update)
    bpy.utils.register_class(CameraSettings)
    bpy.types.Scene.camera_settings = bpy.props.PointerProperty(type=CameraSettings)

def unregister():
    bpy.utils.unregister_class(CAMERA_OT_create_update)
    del bpy.types.Scene.camera_settings