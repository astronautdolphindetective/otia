import bpy
#TODO write function so that files can be saved here

#this still does no work
class SimulateAndSaveOperator(bpy.types.Operator):
    bl_idname = "object.simulate_and_save"
    bl_label = "Simulate and Save"
    bl_options = {'REGISTER', 'UNDO'}

    file_path: bpy.props.StringProperty(
        name="File Path",
        description="Path to save the point cloud data",
        default="",
        subtype='FILE_PATH'
    )

    def execute(self, context):
        if not self.file_path:
            self.report({'ERROR'}, "File path not specified")
            return {'CANCELLED'}

        # Start the animation
        bpy.ops.screen.frame_jump(end=False)
        bpy.ops.screen.animation_play()

        # Wait for animation to complete
        # This is a placeholder; you might want to use a more robust solution
        # like checking the frame number or using handlers to detect when
        # the animation is complete.
        while bpy.context.screen.is_animation_playing:
            bpy.context.view_layer.update()

        # Create and save point clouds for each frame
        for frame in range(context.scene.frame_start, context.scene.frame_end + 1):
            context.scene.frame_set(frame)
            self.perform_scan(context, frame)
        
        logger.info(f"Point clouds saved to: {self.file_path}")
        return {'FINISHED'}

    def perform_scan(self, context, frame):
        # Call the scan operator for the current frame
        bpy.ops.object.custom_raycast_operator()
        
        # Save the point cloud data
        self.save_point_cloud(frame)

    def save_point_cloud(self, frame):
        # Find the last created point cloud object
        point_clouds = [obj for obj in bpy.context.scene.objects if obj.name.startswith("RaycastPoints")]
        if not point_clouds:
            self.report({'ERROR'}, "No point cloud data found")
            return

        obj = point_clouds[-1]  # Get the latest one
        mesh = obj.data
        vertices = np.array([vert.co for vert in mesh.vertices])

        # Create file path for the point cloud
        file_name = f"point_cloud_{frame}.txt"
        file_path = os.path.join(os.path.dirname(self.file_path), file_name)

        # Save to file
        with open(file_path, 'w') as f:
            for vertex in vertices:
                f.write(f"{vertex.x} {vertex.y} {vertex.z}\n")

        logger.info(f"Point cloud for frame {frame} saved to: {file_path}")


def register_datasaver():
    
    bpy.utils.register_class(SimulateAndSaveOperator)

def unregister_datasaver():
    bpy.utils.unregister_class(SimulateAndSaveOperator)
    del SimulateAndSaveOperator