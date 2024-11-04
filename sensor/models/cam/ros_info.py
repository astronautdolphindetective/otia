
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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def save_cam_ros_info(path):
    logger.info("PATH: %s", path)

    info = {
        "publisher": bpy.context.scene.cam_publisher,
        "frame_id": bpy.context.scene.cam_frame_id,
        "hz": bpy.context.scene.cam_hz
    }

    try:
        directory = Path(path)
        directory.mkdir(parents=True, exist_ok=True)
        logger.info("Directory created or already exists: %s", directory)
    except Exception as e:
        logger.error("Failed to create directory: %s", directory)
        raise

    file_path = directory / "ros.json"

    if file_path.is_dir():
        logger.error("A directory with the name 'ros.json' already exists: %s", file_path)
        raise IsADirectoryError(f"A directory with the name 'ros.json' already exists: {file_path}")

    try:
        with open(file_path, 'w') as file:
            json.dump(info, file)
        logger.info("ROS info saved successfully to: %s", file_path)
    except Exception as e:
        logger.error("Failed to write to file: %s", file_path)
        raise