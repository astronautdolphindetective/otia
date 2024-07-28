import bpy


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



class CreateScannerOperator(bpy.types.Operator):
    bl_idname = "object.create_scanner"
    bl_label = "Create Scanner"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        # Retrieve the selected LiDAR model
        selected_lidar = scene.lidar_selection_dropdown
        if selected_lidar:
            # Retrieve parameters for the selected LiDAR model
            parameters = lidar_data[selected_lidar]["parameters"]
            
            # Extract the parameters from the scene
            params = {}
            for param_name in parameters.keys():
                prop_name = f"lidar_{param_name}"
                params[param_name] = getattr(scene, prop_name)

            # Example: Print the parameters to the console
            print("Creating scanner with parameters:", params)

        # Create the scanner base (this part is unchanged)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='ARROWS', location=(0, 0, 0))

        scanner_base = context.active_object
        scene.ray_scanner_base = scanner_base

        return {'FINISHED'}

def register_scanner_creator():
    bpy.utils.register_class(CreateScannerOperator)

def unregister_scanner_creator():
    bpy.utils.unregister_class(CreateScannerOperator)
    del bpy.types.Scene.CreateScannerOperator
