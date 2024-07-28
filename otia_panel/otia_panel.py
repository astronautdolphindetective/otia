import bpy

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
                "description": "Parameter K",
                "default": 3,
                "min": 0
            }
        }
    }
}

# Define the ScannerItem PropertyGroup
class ScannerItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    type: bpy.props.StringProperty(name="Type")

# Define the ScannerList UIList
class OTIA_UL_ScannerList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)

# Define the Panel to create and display sensors
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

        # Template list for displaying created sensors
        layout.template_list("OTIA_UL_ScannerList", "", scene, "scanner_list", scene, "scanner_index")

        # Toggle to show sensor creation settings
        layout.prop(scene, "show_sensor_selection", text="Create sensor", toggle=True)

        if scene.show_sensor_selection:
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
                box.prop(scene, "sensor_mode", text="Mode")
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

            # Create a new scanner item
            scanner_item = scene.scanner_list.add()
            scanner_item.name = sensor_name if sensor_name else "New Scanner"
            scanner_item.type = selected_lidar

            # Create and configure the scanner object in the scene
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.empty_add(type='ARROWS', location=(0, 0, 0))
            scanner_base = context.active_object
            scanner_base.name = sensor_name if sensor_name else "New Scanner"

            if "Sensors" not in bpy.data.collections:
                sensors_collection = bpy.data.collections.new("Sensors")
                bpy.context.scene.collection.children.link(sensors_collection)
            else:
                sensors_collection = bpy.data.collections.get("Sensors")

            sensors_collection.objects.link(scanner_base)
            context.collection.objects.unlink(scanner_base)
        
        return {'FINISHED'}

def register_otia_panel():
    bpy.types.Scene.simulate_file_path = bpy.props.StringProperty(
        name="Save Path",
        description="Path to save the simulated point cloud data",
        default="",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.show_sensor_selection = bpy.props.BoolProperty(
        name="Show Sensor Selection",
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
        items=[(key, value["name"], value["description"]) for key, value in lidar_data.items()]
    )

    bpy.types.Scene.sensor_name = bpy.props.StringProperty(
        name="Sensor Name",
        description="Name of the sensor",
        default="New Sensor"
    )

    bpy.types.Scene.sensor_mode = bpy.props.EnumProperty(
        name="Sensor Mode",
        description="Select the mode of the sensor",
        items=[
            ('HOT', "Hot", "Sensor is in hot mode"),
            ('COLD', "Cold", "Sensor is in cold mode")
        ],
        default='HOT'
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

    bpy.utils.register_class(ScannerItem)
    bpy.types.Scene.scanner_list = bpy.props.CollectionProperty(type=ScannerItem)
    bpy.types.Scene.scanner_index = bpy.props.IntProperty(name="Index")

    bpy.utils.register_class(CreateScannerOperator)
    bpy.utils.register_class(Sensor_Panel)
    bpy.utils.register_class(Otia_Panel)
    bpy.utils.register_class(OTIA_UL_ScannerList)

def unregister_otia_panel():
    bpy.utils.unregister_class(CreateScannerOperator)
    bpy.utils.unregister_class(Sensor_Panel)
    bpy.utils.unregister_class(Otia_Panel)
    bpy.utils.unregister_class(OTIA_UL_ScannerList)
    bpy.utils.unregister_class(ScannerItem)

    del bpy.types.Scene.simulate_file_path
    del bpy.types.Scene.show_sensor_selection
    del bpy.types.Scene.sensor_selection_dropdown
    del bpy.types.Scene.lidar_selection_dropdown
    del bpy.types.Scene.sensor_name
    del bpy.types.Scene.sensor_mode

    for lidar in lidar_data.values():
        for param_name, param_info in lidar["parameters"].items():
            prop_name = f"lidar_{param_name}"
            delattr(bpy.types.Scene, prop_name)

    del bpy.types.Scene.scanner_list
    del bpy.types.Scene.scanner_index

