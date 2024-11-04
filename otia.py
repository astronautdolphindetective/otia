import bpy
import logging
from pathlib import Path
import sys
import os
import json

#begin preprocessing
project_root = "/home/jan/Workspace/lidar_scanner2/otia"
#end preprocessing 
sys.path.append(project_root)

'''
path = Path(bpy.data.filepath).parent
project_root = path / "otia"

print("Blender file path:", bpy.data.filepath)
print("Project root path:", project_root)
print("Checking if project root exists:", project_root.exists())
print("sys.path before:", sys.path)

if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

print("sys.path after:", sys.path)
'''

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bl_info = {
    "name": "orbis terrarum in arca",
    "blender": (4, 2, 1),
    "category": "Object",
}


from otia_panel.otia_panel import register_otia_panel, unregister_otia_panel
from sensor.models.lidar.lidar_creator import register_create_scanner, unregister_create_scanner
from sensor.models.imu.imu_creator import register_create_imu, unregister_create_imu
from sensor.models.cam.camera_creator import regist_camera_creator



def register():
    try:
        regist_camera_creator()
        register_create_scanner()
        register_otia_panel()
        register_create_imu()
    except Exception as e:
        logger.error("Error during registration: %s", e)

    bpy.types.Scene.ray_scanner_base = bpy.props.PointerProperty(
        name="Scanner Base",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'EMPTY'
    )
    bpy.types.Scene.ray_scanner_path = bpy.props.PointerProperty(
        name="Scanner Path",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'CURVE'
    )

def unregister():
    try:
        unregister_create_scanner()
        unregister_otia_panel()
        unregister_create_imu()
        
    except Exception as e:
        logger.error("Error during unregistration: %s", e)

    del bpy.types.Scene.ray_scanner_base
    del bpy.types.Scene.ray_scanner_path


if __name__ == "__main__":
    register()
