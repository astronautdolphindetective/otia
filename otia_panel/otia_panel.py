import bpy
import json
from otia_panel.sensor_scrollbar import register_mock_data, unregister_mock_data

# JSON data
lidar_data = {
    "livox_mid40": {
        "name": "Livox Mid 40",
        "description": "blablabla",
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
                "description": "A",
                "default": 2,
                "min": 0
            }
        }
    },
    "velodyne_hdl": {
        "name": "Velodyne HDL64",
        "description": "blablabla",
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
                "description": "K",
                "default": 3,
                "min": 0
            }
        }
    }
}

class Base_Panel(bpy.types.Panel):
    bl_label = "Base"
    bl_idname = "OBJECT_PT_base_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Otia'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Bases")
        layout.template_list("OTIA_UL_MockDataList", "", scene, "mock_data_collection", scene, "mock_data_index")

        layout.prop(scene, "show_accordion_settings", text="Create Base", toggle=True)

        if scene.show_accordion_settings:
            box = layout.box()
            box.prop(scene, "scanner_selection_dropdown", text="Select Option")
            box.operator("object.create_scanner", text="Create Base")
            box.prop(scene, "ray_scanner_path", text="Path")
            box.operator("object.follow_path", text="Follow Path")

            box.prop(scene, "ray_dist", text="Max Distance")
            box.prop(scene, "ray_scans", text="Scans")
            box.prop(scene, "ray_density", text="Points per scan")
            box.prop(scene, "ray_k", text="Leaves")
            box.operator("object.custom_raycast_operator", text="Perform Raycast")

class Sensor_Panel(bpy.types.Panel):
    bl_label = "Sensor"
    bl_idname = "OBJECT_PT_sensor_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Otia'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Sensors")
        layout.template_list("OTIA_UL_MockDataList", "", scene, "mock_data_collection", scene, "mock_data_index")

        layout.prop(scene, "show_sensor_selection", text="Create sensor", toggle=True)

        if scene.show_sensor_selection:
            box = layout.box()
            box.prop(scene, "sensor_selection_dropdown", text="Type")

            selected_sensor = scene.sensor_selection_dropdown
            if selected_sensor == 'LIDAR':
                box.prop(scene, "lidar_selection_dropdown", text="Model")
                selected_lidar = scene.lidar_selection_dropdown
                if selected_lidar:
                    parameters = lidar_data[selected_lidar]["parameters"]
                    for param_name, param_info in parameters.items():
                        prop_name = f"lidar_{param_name}"
                        box.prop(scene, prop_name, text=param_info["description"])
                box.operator("object.create_scanner", text="Create Scanner")

class Otia_Panel(bpy.types.Panel):
    bl_label = "Simulate"
    bl_idname = "OBJECT_PT_otial_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Otia'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "simulate_file_path", text="Save Path")
        layout.operator("object.simulate_and_save", text="Simulate").file_path = scene.simulate_file_path

def register_otia_panel():
    bpy.types.Scene.simulate_file_path = bpy.props.StringProperty(
        name="Save Path",
        description="Path to save the simulated point cloud data",
        default="",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.show_accordion_settings = bpy.props.BoolProperty(
        name="Show Additional Settings",
        description="Toggle to show or hide additional settings",
        default=False
    )
    
    bpy.types.Scene.show_sensor_selection = bpy.props.BoolProperty(
        name="Select a sensor",
        description="Toggle to show or hide sensor selection",
        default=False
    )

    bpy.types.Scene.sensor_selection_dropdown = bpy.props.EnumProperty(
        name="Sensor Type",
        description="Select a sensor type",
        items=[('CAM', "Camera", ""), ('IMU', "IMU", ""), ('LIDAR', "LiDAR", "")]
    )

    bpy.types.Scene.lidar_selection_dropdown = bpy.props.EnumProperty(
        name="LiDAR Model",
        description="Select a LiDAR model",
        items=[('livox_mid40', "Livox Mid 40", ""), ('velodyne_hdl', "Velodyne HDL64", "")]
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

    bpy.utils.register_class(Otia_Panel)
    bpy.utils.register_class(Sensor_Panel)
    bpy.utils.register_class(Base_Panel)

    register_mock_data()

def unregister_otia_panel():
    bpy.utils.unregister_class(Otia_Panel)
    bpy.utils.unregister_class(Sensor_Panel)
    bpy.utils.unregister_class(Base_Panel)

    unregister_mock_data()
    del bpy.types.Scene.simulate_file_path
    del bpy.types.Scene.show_accordion_settings
    del bpy.types.Scene.show_sensor_selection
    del bpy.types.Scene.sensor_selection_dropdown
    del bpy.types.Scene.lidar_selection_dropdown

    for lidar in lidar_data.values():
        for param_name in lidar["parameters"].keys():
            prop_name = f"lidar_{param_name}"
            delattr(bpy.types.Scene, prop_name)

