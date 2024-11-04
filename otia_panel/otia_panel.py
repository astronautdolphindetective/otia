import bpy
import os
import json
import logging
from pathlib import Path
import sys


#begin preprocessing
project_root = "/home/jan/Workspace/lidar_scanner2/otia"
#end preprocessing 
sys.path.append(project_root)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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

def render_cameras(scene):
    # Get the Cameras collection
    camera_collection = bpy.data.collections.get("Cameras")
    if not camera_collection:
        logger.error("Cameras collection not found")
        return
    
    # Ensure output path is set
    output_folder = scene.folder_path
    if not output_folder or not os.path.isdir(output_folder):
        logger.error("Output folder path is not set or does not exist")
        return

    # Ensure render settings are configured correctly
    scene.render.image_settings.file_format = 'PNG'
    scene.render.use_file_extension = True
    
    # Render all frames for each camera
    for obj in camera_collection.objects:
        if obj.type == 'CAMERA':
            # Create a directory for the current camera
            camera_folder = os.path.join(output_folder, "cam", obj.name)
            os.makedirs(camera_folder, exist_ok=True)

            # Set the current camera
            scene.camera = obj

            # Render each frame
            for frame_number in range(scene.frame_start, scene.frame_end + 1):
                scene.frame_set(frame_number)
                render_path = os.path.join(camera_folder, f"{frame_number}.png")
                scene.render.filepath = render_path
                
                # Perform rendering
                logger.info(f"Rendering camera: {obj.name} at frame {frame_number} to {render_path}")
                bpy.ops.render.render(write_still=True)


def simulate(scene):
    logger.info("STARTING THE SIMULATION")
    scene.simulation_running = True
    # Ensure the simulation handler runs properly
    if simulate not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(simulate)

    current_frame = scene.frame_current
    end_frame = scene.frame_end

    bpy.ops.object.trigger_all_scans()

    if current_frame >= end_frame:
        # Stop the simulation
        bpy.ops.screen.animation_cancel()
        if simulate in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(simulate)
        logger.info("Simulation ended at frame %d", current_frame)
        
        # Render all imus and cameras 
        bpy.ops.object.trigger_all_imus()
        render_cameras(scene)
    
    logger.info("FINISHED THE SIMULATION")
    scene.simulation_running = False


class TriggerAllImuOperator(bpy.types.Operator):
    bl_idname = "object.trigger_all_imus"
    bl_label = "Trigger All imu"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        logger.info("Triggering all imus")

        imu_collection = bpy.data.collections.get("IMU")
        if not imu_collection:
            self.report({'ERROR'}, "IMU collection not found")
            return {'CANCELLED'}

        for obj in imu_collection.objects:
            if obj.type == 'EMPTY':
                operator_idname = f"object.imu_{obj.name}"
                logger.info("Triggering operator: %s", operator_idname)
                try:
                    eval(f"bpy.ops.object.imu_{obj.name}()")
                    logger.info(f"Triggered imu reading for {obj.name}")
                except Exception as e:
                    logger.error(f"Failed to trigger scan for {obj.name}: {str(e)}")

        return {'FINISHED'}

class TriggerAllScansOperator(bpy.types.Operator):
    bl_idname = "object.trigger_all_scans"
    bl_label = "Trigger All Scans"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        logger.info("Triggering all scans")

        lidar_collection = bpy.data.collections.get("LiDAR")
        if not lidar_collection:
            self.report({'ERROR'}, "LiDAR collection not found")
            return {'CANCELLED'}

        for obj in lidar_collection.objects:
            if obj.type == 'EMPTY':
                operator_idname = f"object.custom_raycast_{obj.name}"
                logger.info("Triggering operator: %s", operator_idname)
                try:
                    eval(f"bpy.ops.object.custom_raycast_{obj.name}()")
                    logger.info(f"Triggered scan for {obj.name}")
                except Exception as e:
                    logger.error(f"Failed to trigger scan for {obj.name}: {str(e)}")

        return {'FINISHED'}

class SetFolderPathOperator(bpy.types.Operator):
    bl_idname = "object.set_folder_path"
    bl_label = "Set Folder Path"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        context.scene.folder_path = self.directory
        logger.info(f"Folder path set to: {self.directory}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ControlPanel(bpy.types.Panel):
    bl_label = "Control Panel"
    bl_idname = "OBJECT_PT_control_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Otia'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Control Panel")
        layout.operator("object.trigger_all_scans", text="Single Scan")
        layout.prop(context.scene, "milliseconds_per_frame", text="Milliseconds per Frame")
        layout.prop(context.scene, "folder_path", text="Folder Path")
        layout.operator("object.set_folder_path", text="Select Output Folder")
        layout.operator("object.start_simulation", text="Start Simulation")

class StartSimulationOperator(bpy.types.Operator):
    bl_idname = "object.start_simulation"
    bl_label = "Start Simulation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Set the current frame to the start frame
        scene = context.scene
        scene.frame_set(scene.frame_start)
        
        # Add the frame change handler
        if simulate not in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.append(simulate)
        
        # Start the animation playback
        bpy.ops.screen.animation_play()
        
        return {'FINISHED'}

class StopSimulationOperator(bpy.types.Operator):
    bl_idname = "object.stop_simulation"
    bl_label = "Stop Simulation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.screen.animation_cancel()
        if simulate in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(simulate)
        return {'FINISHED'}

class SensorPanel(bpy.types.Panel):
    bl_label = "Sensor"
    bl_idname = "OBJECT_PT_sensor_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Otia'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Sensors")

        box = layout.box()
        box.prop(scene, "sensor_selection_dropdown", text="Sensor Type")

        selected_sensor = scene.sensor_selection_dropdown
        if selected_sensor == 'LIDAR':
            box.prop(scene, "lidar_selection_dropdown", text="LiDAR Model")
            selected_lidar = scene.lidar_selection_dropdown
            if selected_lidar:
                parameters = lidar_data[selected_lidar]["parameters"]
                for param_name, param_info in parameters.items():
                    prop_name = f"lidar_{param_name}"
                    box.prop(scene, prop_name, text=param_info["description"])
                box.prop(scene, "lidar_name", text="Sensor Name")
                box.prop(scene, "lidar_frame_id",text="ROS Frame Id")
                box.prop(scene, "lidar_publisher",text="ROS publisher")
                box.prop(scene, "lidar_hz",text="HZ")
            box.operator("object.create_scanner", text="Create Scanner")

        elif selected_sensor == 'IMU':
            box.prop(scene, "imu_name", text="Sensor Name")
            box.prop(scene, "imu_frame_id",text="ROS Frame Id")
            box.prop(scene, "imu_publisher",text="ROS publisher")
            box.prop(scene, "imu_hz",text="HZ")
            box.operator("object.create_imu", text="Create IMU")

        elif selected_sensor == 'CAM':
            camera_settings = scene.camera_settings

            box.prop(camera_settings, "lens")
            box.prop(camera_settings, "sensor_width")
            box.prop(camera_settings, "location")
            box.prop(camera_settings, "rotation")
            box.prop(camera_settings, "camera_type")
            box.prop(camera_settings, "clip_start")
            box.prop(camera_settings, "clip_end")
            box.prop(camera_settings, "shift_x")
            box.prop(camera_settings, "shift_y")
            box.prop(camera_settings, "sensor_fit")
            box.prop(scene, "cam_frame_id")
            box.prop(scene, "cam_publisher")
            box.prop(scene, "cam_hz")
            box.prop(scene, "cam_name", text="Camera Name")
            box.operator("camera.create_update")

def register_properties():
    bpy.types.Scene.folder_path = bpy.props.StringProperty(
        name="Folder Path",
        description="Path to save files",
        default=str(project_root)
    )

    bpy.types.Scene.sensor_selection_dropdown = bpy.props.EnumProperty(
        name="Sensor Type",
        description="Select a sensor type",
        items=[('CAM', "Camera", ""), ('IMU', "IMU", ""), ('LIDAR', "LiDAR", "")]
    )

    bpy.types.Scene.lidar_selection_dropdown = bpy.props.EnumProperty(
        name="LiDAR Model",
        description="Select a LiDAR model",
        items=[(key, value["name"], value["description"]) for key, value in lidar_data.items()]
    )

    bpy.types.Scene.lidar_name = bpy.props.StringProperty(
        name="Sensor Name",
        description="Name of the sensor",
        default="lidar"
    )

    bpy.types.Scene.cam_name = bpy.props.StringProperty(
        name="Sensor Name",
        description="Name of the sensor",
        default="cam"
    )

    bpy.types.Scene.imu_name = bpy.props.StringProperty(
        name="Sensor Name",
        description="Name of the sensor",
        default="imu"
    )

    bpy.types.Scene.lidar_frame_id = bpy.props.StringProperty(
        name="ROS Frame Id",
        description="frame_id",
        default="base_index"
    )

    bpy.types.Scene.lidar_publisher = bpy.props.StringProperty(
        name="ROS Publisher",
        description="ROS Publisher",
        default="publisher/lidar"
    )

    bpy.types.Scene.imu_frame_id = bpy.props.StringProperty(
        name="ROS Frame Id",
        description="frame_id",
        default="base_index"
    )

    bpy.types.Scene.imu_publisher = bpy.props.StringProperty(
        name="ROS Publisher",
        description="ROS Publisher",
        default="publisher/imu"
    )

    bpy.types.Scene.cam_frame_id = bpy.props.StringProperty(
        name="ROS Frame Id",
        description="frame_id",
        default="base_index"
    )

    bpy.types.Scene.cam_publisher = bpy.props.StringProperty(
        name="ROS Publisher",
        description="ROS Publisher",
        default="publisher/imu"
    )
    bpy.types.Scene.imu_hz = bpy.props.IntProperty(
        name="IMU Frequency",
        description="Frequency of IMU data publication in Hz",
        default=10,
        min=0,
        max=1000,
    )

    bpy.types.Scene.lidar_hz = bpy.props.IntProperty(
        name="LiDAR Frequency",
        description="Frequency of LiDAR data publication in Hz",
        default=10,
        min=0,
        max=1000
    )

    bpy.types.Scene.cam_hz = bpy.props.IntProperty(
        name="Camera Frequency",
        description="Frequency of Camera data publication in Hz",
        default=10,
        min=0,
        max=1000,
    )

    bpy.types.Scene.milliseconds_per_frame= bpy.props.IntProperty(
        name="Milliseconds per Frame",
        description="Milliseconds per Frame",
        default=10,
        min=1,
        max=1000,
    )

    bpy.types.Scene.simulation_running = bpy.props.BoolProperty(
        name="Simulation is running",
        description="turns true if simulation is running",
        default=False
    )

    for lidar in lidar_data.values():
        for param_name, param_info in lidar["parameters"].items():
            prop_name = f"lidar_{param_name}"
            if param_info["type"] == "float":
                setattr(bpy.types.Scene, prop_name, bpy.props.FloatProperty(
                    name=param_info["description"],
                    description=param_info["description"],
                    default=param_info["default"],
                    min=param_info["min"]
                ))
            elif param_info["type"] == "int":
                setattr(bpy.types.Scene, prop_name, bpy.props.IntProperty(
                    name=param_info["description"],
                    description=param_info["description"],
                    default=param_info["default"],
                    min=param_info["min"]
                ))

def unregister_properties():
    del bpy.types.Scene.folder_path
    del bpy.types.Scene.sensor_selection_dropdown
    del bpy.types.Scene.lidar_selection_dropdown
    del bpy.types.Scene.sensor_name

    for lidar in lidar_data.values():
        for param_name, param_info in lidar["parameters"].items():
            prop_name = f"lidar_{param_name}"
            delattr(bpy.types.Scene, prop_name)

def register_otia_panel():
    register_properties()
    bpy.utils.register_class(TriggerAllScansOperator)
    bpy.utils.register_class(TriggerAllImuOperator)
    bpy.utils.register_class(SensorPanel)
    bpy.utils.register_class(ControlPanel)
    bpy.utils.register_class(SetFolderPathOperator)
    bpy.utils.register_class(StartSimulationOperator)
    bpy.utils.register_class(StopSimulationOperator)

def unregister_otia_panel():
    bpy.utils.unregister_class(SensorPanel)
    bpy.utils.unregister_class(TriggerAllScansOperator)
    bpy.utils.unregister_class(TriggerAllImuOperator)
    bpy.utils.unregister_class(ControlPanel)
    bpy.utils.unregister_class(SetFolderPathOperator)
    bpy.utils.unregister_class(StartSimulationOperator)
    bpy.utils.unregister_class(StopSimulationOperator)
    unregister_properties()
