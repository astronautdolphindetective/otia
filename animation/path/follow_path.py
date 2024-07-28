import bpy

#this is good
class FollowPathOperator(bpy.types.Operator):
    bl_idname = "object.follow_path"
    bl_label = "Follow Path"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scanner_base = context.scene.ray_scanner_base
        path = context.scene.ray_scanner_path

        if scanner_base is None or scanner_base.type != 'EMPTY':
            self.report({'ERROR'}, "No active empty object as scanner base")
            return {'CANCELLED'}

        if path is None or path.type != 'CURVE':
            self.report({'ERROR'}, "No active curve object as path")
            return {'CANCELLED'}

        # Remove existing constraints to avoid conflicts
        for constraint in scanner_base.constraints:
            scanner_base.constraints.remove(constraint)

        # Add Follow Path constraint
        follow_path_constraint = scanner_base.constraints.new(type='FOLLOW_PATH')
        follow_path_constraint.target = path
        follow_path_constraint.use_curve_follow = True
        follow_path_constraint.use_fixed_location = True
        follow_path_constraint.forward_axis = 'FORWARD_Z'
        follow_path_constraint.up_axis = 'UP_Y'
        follow_path_constraint.offset_factor = 0

        # Animate the Follow Path constraint
        scene = context.scene
        frame_start = scene.frame_start
        frame_end = scene.frame_end

        follow_path_constraint.offset_factor = 0
        follow_path_constraint.keyframe_insert(data_path="offset_factor", frame=frame_start)

        follow_path_constraint.offset_factor = 1
        follow_path_constraint.keyframe_insert(data_path="offset_factor", frame=frame_end)

        logger.info("Scanner is set to follow path: %s", path.name)

        return {'FINISHED'}