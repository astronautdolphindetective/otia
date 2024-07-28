import bpy

class CreateScannerOperator(bpy.types.Operator):
    bl_idname = "object.create_scanner"
    bl_label = "Create Scanner"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

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