import bpy
import logging
from pathlib import Path
import sys

path = Path(bpy.data.filepath).parent
project_root = path / "otia"

print("Blender file path:", bpy.data.filepath)
print("Project root path:", project_root)
print("Checking if project root exists:", project_root.exists())
print("sys.path before:", sys.path)

if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

print("sys.path after:", sys.path)

#from sensor.models.lidar.scanner_base import register_base_scanner, unregister_base_scanner
from sensor.sensor_selection import register_sensor_selection, unregister_sensor_selection
from otia_panel.otia_panel import register_otia_panel, unregister_otia_panel
from sensor.models.lidar.lidar_creator import register_create_scanner, unregister_create_scanner
from sensor.models.cam.camera_creator import regist_camera_creator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bl_info = {
    "name": "orbis terrarum in arca",
    "blender": (4, 2, 0),
    "category": "Object",
}

def frame_change_handler(scene):
    bpy.ops.object.custom_raycast_operator()

def register():
    try:
        regist_camera_creator()
        register_create_scanner()
        register_otia_panel()
        #register_base_scanner()
        register_sensor_selection()
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
    bpy.app.handlers.frame_change_post.append(frame_change_handler)

def unregister():
    try:
        unregister_create_scanner()
        unregister_otia_panel()
        #unregister_base_scanner()
        unregister_sensor_selection()
    except Exception as e:
        logger.error("Error during unregistration: %s", e)

    del bpy.types.Scene.ray_scanner_base
    del bpy.types.Scene.ray_scanner_path
    del bpy.types.Scene.simulate_file_path

    bpy.app.handlers.frame_change_post.remove(frame_change_handler)

if __name__ == "__main__":
    register()
