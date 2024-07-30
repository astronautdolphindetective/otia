import bpy
import os
import json
import logging
import numpy as np
from pathlib import Path

path = Path(bpy.data.filepath).parent
project_root = path / "otia"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def save_imu_data(imu_data, folder_path, file_name="imu.npy"):
    """Saves the IMU data as a NumPy file."""
    try:
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        imu_array = np.array(imu_data)
        file_path = os.path.join(folder_path, "IMU", file_name)
        np.save(file_path, imu_array)
        logger.info(f"IMU data saved to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save IMU data: {e}")

def create_imu_operator(imu_name):
    """Creates a custom IMU operator for the given IMU name."""
    class ImuOperator(bpy.types.Operator):
        bl_idname = f"object.imu_{imu_name}"
        bl_label = f"IMU {imu_name}"
        bl_options = {'REGISTER', 'UNDO'}

        def execute(self, context):
            return self.get_imu(context)

        def get_imu(self, context):
            """Extracts IMU data and position for the given object."""
            scene = context.scene
            outpath = scene.folder_path
            imu_object = bpy.data.objects.get(imu_name)

            if not imu_object:
                self.report({'ERROR'}, f"IMU object {imu_name} not found")
                return {'CANCELLED'}

            frame_start = scene.frame_start
            frame_end = scene.frame_end
            frame_rate = scene.render.fps

            positions = []
            rotations = []
            accelerations = []
            angular_velocities = []

            previous_position = None
            previous_rotation = None

            for frame in range(frame_start, frame_end + 1):
                scene.frame_set(frame)
                matrix_world = imu_object.matrix_world
                current_position = np.array(matrix_world.translation)
                current_rotation = np.array(matrix_world.to_euler())

                positions.append(current_position)
                rotations.append(current_rotation)

                if previous_position is not None:
                    velocity = (current_position - previous_position) * frame_rate
                    previous_velocity = (previous_position - np.array(positions[-2])) * frame_rate if len(positions) > 1 else velocity
                    acceleration = (velocity - previous_velocity) * frame_rate
                    accelerations.append(acceleration)
                else:
                    accelerations.append(np.array([0, 0, 0]))

                if previous_rotation is not None:
                    # Calculate the difference in rotation between frames
                    delta_rotation = current_rotation - previous_rotation
                    angular_velocity = delta_rotation * frame_rate
                    angular_velocities.append(angular_velocity)
                else:
                    angular_velocities.append(np.array([0, 0, 0]))

                previous_position = current_position
                previous_rotation = current_rotation

            # Convert lists to arrays for saving
            imu_data = {
                "positions": np.array(positions),
                "rotations": np.array(rotations),
                "accelerations": np.array(accelerations),
                "angular_velocities": np.array(angular_velocities),
                "frame_rate": frame_rate
            }

            # Create a folder for the IMU if it doesn't exist
            imu_folder = os.path.join(outpath, imu_name)
            save_imu_data(imu_data, imu_folder, f"{imu_name}_imu_data.npy")

            return {'FINISHED'}

    bpy.utils.register_class(ImuOperator)
    return ImuOperator

class CreateImuOperator(bpy.types.Operator):
    """Operator to create a new IMU sensor."""
    bl_idname = "object.create_imu"
    bl_label = "Create IMU"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        sensor_name = context.scene.sensor_name

        logger.info("imu: %s", sensor_name)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='ARROWS', location=(0, 0, 0))
        imu_base = context.active_object
        imu_base.name = sensor_name if sensor_name else "New IMU"

        # Create a custom collection if it doesn't exist
        if "IMU" not in bpy.data.collections:
            sensors_collection = bpy.data.collections.new("IMU")
            bpy.context.scene.collection.children.link(sensors_collection)
        else:
            sensors_collection = bpy.data.collections.get("IMU")

        # Add the IMU to the collection
        sensors_collection.objects.link(imu_base)
        context.collection.objects.unlink(imu_base)

        # Create a custom operator for the new IMU
        create_imu_operator(sensor_name)

        # Update the UI
        context.area.tag_redraw()
        context.view_layer.update()

        return {'FINISHED'}

def register_create_imu():
    bpy.utils.register_class(CreateImuOperator)

def unregister_create_imu():
    bpy.utils.unregister_class(CreateImuOperator)

# Register properties and other operators, panels, etc., as needed.
