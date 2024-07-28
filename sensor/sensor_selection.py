import bpy

# Define the dropdown items
dropdown_items = [
    ('CAM', "Camera", "a camera"),
    ('IMU', "IMU", "an imu"),
    ('LIDAR', 'LiDAR', 'a lidar scanner')
]

def register_sensor_selection():
    bpy.types.Scene.sensor_selection_dropdown = bpy.props.EnumProperty(
        name="sensor selection",
        description="Sensor Selection",
        items=dropdown_items,
    )

def unregister_sensor_selection():
    del bpy.types.Scene.sensor_selection_dropdown
