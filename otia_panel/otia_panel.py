import bpy
import logging



logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# JSON data for LiDAR models
lidar_data = {
    "livox_mid40": {
        "name": "Livox Mid 40",
        "description": "Livox Mid 40 description",
        "parameters": {
            "max_distance": {
                "type": "float",
                "description": "Maximum Distance",
                "default": 10.0,
                "min": 0.1
            },
            "scans": {
                "type": "int",
                "description": "Number of Scans",
                "default": 5,
                "min": 1
            },
            "density": {
                "type": "int",
                "description": "Point Density",
                "default": 10,
                "min": 1
            },
            "k": {
                "type": "int",
                "description": "Parameter K",
                "default": 2,
                "min": 0
            }
        }
    },
    "velodyne_hdl": {
        "name": "Velodyne HDL64",
        "description": "Velodyne HDL64 description",
        "parameters": {
            "max_distance": {
                "type": "float",
                "description": "Maximum Distance",
                "default": 20.0,
                "min": 0.1
            },
            "scans": {
                "type": "int",
                "description": "Number of Scans",
                "default": 10,
                "min": 1
            },
            "density": {
                "type": "int",
                "description": "Point Density",
                "default": 20,
                "min": 1
            },
            "k": {
                "type": "int",
                "description": "XXXXXX",
                "default": 3,
                "min": 0
            },
            "X": {
                "type": "int",
                "description": "XXXXXX",
                "default": 3,
                "min": 0
            }
        }
    }
}


class TriggerAllScansOperator(bpy.types.Operator):
    bl_idname = "object.trigger_all_scans"
    bl_label = "Trigger All Scans"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        logger.info("Triggering all scans")

        # Ensure the LiDAR collection exists
        lidar_collection = bpy.data.collections.get("LiDAR")
        if not lidar_collection:
            self.report({'ERROR'}, "LiDAR collection not found")
            return {'CANCELLED'}

        # Loop through all objects in the LiDAR collection

        for e in dir(bpy.ops.object):
            logger.info("e: %s", e)

        for obj in lidar_collection.objects:
            if obj.type == 'EMPTY':
                operator_idname = f"object.custom_raycast_{obj.name}"
                logger.info("Triggering operator: %s", operator_idname)
                try:
                    # Call the operator
                    eval(f"bpy.ops.object.custom_raycast_{obj.name}()")
                    logger.info(f"Triggered scan for {obj.name}")
                except Exception as e:
                    logger.error(f"Failed to trigger scan for {obj.name}: {str(e)}")

        return {'FINISHED'}


class ControlPanel(bpy.types.Panel):
    bl_label = "Control Panel"
    bl_idname = "OBJECT_PT_control_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Otia'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Control Panel")
        layout.operator("object.trigger_all_scans", text="Scan")


# Define the Panel to create and display sensors
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

        # Show sensor creation settings
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
            box.prop(scene, "sensor_name", text="Sensor Name")
            box.operator("object.create_scanner", text="Create Scanner")

        elif selected_sensor == 'CAM':
            camera_settings = scene.camera_settings

            box.prop(camera_settings, "name", text="Camera Name")
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

            box.operator("camera.create_update")

def register_properties():
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

    bpy.types.Scene.sensor_name = bpy.props.StringProperty(
        name="Sensor Name",
        description="Name of the sensor",
        default="New Sensor"
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
    del bpy.types.Scene.sensor_selection_dropdown
    del bpy.types.Scene.lidar_selection_dropdown
    del bpy.types.Scene.sensor_name
    del bpy.types.Scene.sensor_mode

    for lidar in lidar_data.values():
        for param_name, param_info in lidar["parameters"].items():
            prop_name = f"lidar_{param_name}"
            delattr(bpy.types.Scene, prop_name)

def register_otia_panel():
    register_properties()
    bpy.utils.register_class(TriggerAllScansOperator)
    bpy.utils.register_class(ControlPanel)
    bpy.utils.register_class(SensorPanel)

def unregister_otia_panel():
    bpy.utils.unregister_class(SensorPanel)
    bpy.utils.unregister_class(TriggerAllScansOperator)
    bpy.utils.unregister_class(ControlPanel)
    unregister_properties()
