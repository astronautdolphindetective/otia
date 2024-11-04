
import bpy
import os
import json
import bmesh
import logging
import numpy as np
from mathutils import Vector
from pathlib import Path
import sys


project_root = '/home/jan/Workspace/lidar_scanner/otia'
sys.path.append(project_root)




print("sys.path after:", sys.path)


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def save_imu_ros_info(path):
    logger.info("PATH: %s", path)

    info = {
        "publisher": bpy.context.scene.imu_publisher,
        "frame_id": bpy.context.scene.imu_frame_id,
        "hz": bpy.context.scene.imu_hz
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